import json
from typing import Any, Dict

from app.apis.evolution import send_message
from app.core.distributed_lock import DistributedLock
from app.core.logger_config import get_logger
from app.database.manipulations import ia_manipulations, lead_manipulations
from app.schemas.webhook import WebhookPayload
from app.service.llm_response import IAresponse
from app.service.quebra_mensagem import calculate_typing_delay, quebrar_mensagens
from app.service.sanitize import sanitize_dict

log = get_logger()


# ===============================================================
#  🔹 PROCESSAMENTO PRINCIPAL DO WEBHOOK (SINCRONO)
# ===============================================================
def process_webhook_data(data: Dict[str, Any]) -> None:
    """
    Processa o payload do Evolution API usando validação Pydantic e
    aplica regras do fluxo de IA, Lead e Respostas.
    """

    log.info("📩 Webhook recebido do Evolution")
    log.debug(json.dumps(data, indent=2, ensure_ascii=False, default=str))

    try:
        # 1️⃣ Sanitizar o payload
        data = sanitize_dict(data)

        # 2️⃣ Validar estrutura via Pydantic
        payload = WebhookPayload(**data)

        ia_name = payload.instance
        ia_phone = payload.sender.split("@")[0]

        # 3️⃣ Buscar IA na base interna
        ia_infos = ia_manipulations.filter_ia(ia_phone)
        if not ia_infos:
            raise Exception("IA não encontrada")
        if not ia_infos.status:
            raise Exception(f"IA {ia_infos.nome} está inativa")

        # 4️⃣ Extrair dados
        webhook_data = payload.data
        message_id = webhook_data.key.id
        message_type = webhook_data.messageType

        mensagem_texto = _processar_conteudo(
            webhook_data.model_dump(),
            ia_name,
            message_id,
            message_type,
            ia_infos,
        )

        if not mensagem_texto:
            raise Exception(f"Conteúdo da mensagem não reconhecido: {message_type=}")

        lead_name = webhook_data.pushName or "Usuário"
        lead_phone = webhook_data.key.remoteJid.split("@")[0]

        log.info(f"👤 Lead: {lead_name} ({lead_phone})")
        log.info(f"💬 Mensagem recebida: {mensagem_texto}")
        # 5️⃣ Seção crítica protegida por lock distribuído (concorrência)

        lock_key = f"webhook_processing:{lead_phone}"
        with DistributedLock(lock_key, timeout=30):
            lead_db = _gerenciar_lead(lead_phone, lead_name, ia_infos, mensagem_texto)

            # 6️⃣ Resposta da IA
            resposta_ia, historico = _gerar_resposta_ia(
                ia_infos,
                mensagem_texto,
                lead_db.message,
                lead_db.resume,
            )

            # 7️⃣ Enviar resposta
            _responder_lead(ia_name, lead_phone, resposta_ia)

            # 8️⃣ Contabilizar interações
            total_interacoes = _contar_interacoes(historico)
            log.info(f"📊 Total de interações: {total_interacoes}")

            # 9️⃣ Gerar resumo quando necessário
            resumo = _gerar_resumo_periodico(total_interacoes, historico, ia_infos)

            # 🔟 Atualizar lead com a resposta e o resumo
            _atualizar_lead_db(lead_db.id, resposta_ia, resumo)

            log.success(f"✅ Lead {lead_db.name} processado com sucesso.")

    except Exception as ex:
        log.error(f"❌ Erro no processamento: {ex}", exc_info=True)


# ===============================================================
#  🔹 FUNÇÕES INTERNAS (organização e clareza)
# ===============================================================


def _processar_conteudo(
    data: Dict[str, Any],
    instance: str,
    message_id: str,
    message_type: str,
    ia_infos: object,
) -> str:
    """Processa conteúdo da mensagem recebida."""
    message = data.get("message", {})

    if message_type == "conversation":
        return message.get("conversation", "")

    if message_type == "extendedTextMessage":
        return message.get("extendedTextMessage", {}).get("text", "")

    if message_type == "imageMessage":
        log.info("🖼️ Imagem recebida")
        return "Imagem recebida"

    if message_type == "audioMessage":
        log.info("🎧 Áudio recebido")
        return "Mensagem de áudio"

    if message_type == "documentWithCaptionMessage":
        log.info("📄 Documento recebido")
        try:
            mime_type = (
                message.get("documentWithCaptionMessage", {})
                .get("message", {})
                .get("documentMessage", {})
                .get("mimeType", "")
            )
            tipo = mime_type.split("/")[1] if "/" in mime_type else "desconhecido"
            return f"Documento recebido ({tipo})"
        except Exception:
            return "Documento recebido (tipo desconhecido)"

    log.warning(f"⚠️ Tipo não reconhecido: {message_type}")
    return ""


def _gerenciar_lead(lead_phone, lead_name, ia_infos, mensagem_texto):
    """Busca ou cria Lead e mantém histórico."""
    mensagem_atual = {
        "role": "user",
        "name": lead_name,
        "content": mensagem_texto,
    }

    lead_db = lead_manipulations.filter_lead(lead_phone, mensagem_atual)

    if not lead_db:
        lead_db = lead_manipulations.new_lead(
            ia_infos.id,
            lead_phone,
            lead_name,
            [mensagem_atual],
        )
        log.info(f"🆕 Novo lead criado: {lead_name} ({lead_phone})")

    return lead_db


def _gerar_resposta_ia(ia_infos, mensagem_texto, historico, resumo):
    """Chama a IA e gera resposta."""
    api_key = ia_infos.ia_config.credentials.get("api_key")
    ia_model = ia_infos.ia_config.credentials.get("ia_model", "")
    system_prompt = ia_infos.active_prompts

    if not system_prompt:
        raise Exception("Nenhum prompt ativo configurado")

    llm = IAresponse(api_key, ia_model, system_prompt.prompt_text, resumo)

    resposta = llm.generate_response(mensagem_texto, historico)
    if not resposta:
        raise Exception("IA não gerou resposta")

    return resposta, historico


def _responder_lead(instance, phone, resposta):
    """Envia a resposta, respeitando delay e possíveis quebras."""
    mensagens = quebrar_mensagens(resposta) or [resposta]

    for msg in mensagens:
        delay = calculate_typing_delay(msg)
        log.info(f"⏱ Delay: {delay}s")
        log.info(f"💬 Enviando: {msg}")
        send_message(instance, phone, msg, delay)


def _contar_interacoes(historico):
    """Conta alternância entre user/assistant."""
    total = 0
    ultimo = None
    for m in historico:
        if m["role"] != ultimo:
            total += 1
            ultimo = m["role"]
    return total


def _gerar_resumo_periodico(total, historico, ia_infos):
    """Gera resumo se chegou no número de interações."""
    for n in range(20, 26):
        if total % n == 0:
            log.info(f"🧠 Gerando resumo (interações={total})")
            llm = IAresponse(
                ia_infos.ia_config.credentials.get("api_key"),
                ia_infos.ia_config.credentials.get("ia_model"),
                ia_infos.active_prompts.prompt_text,
                None,
            )
            return llm.generate_resume(historico)
    return None


def _atualizar_lead_db(lead_id, resposta, resumo):
    """Atualiza histórico e possível resumo."""
    update_data = {
        "role": "assistant",
        "content": resposta,
    }
    ok = lead_manipulations.update_lead(lead_id, update_data, resumo)

    if not ok:
        raise Exception(f"Falha ao atualizar lead {lead_id}")
