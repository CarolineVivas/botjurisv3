"""
Processamento de webhooks do Evolution API.

Módulo responsável por processar mensagens recebidas via webhook,
gerenciar leads, gerar respostas da IA e enviar mensagens.
"""

import json
from typing import Dict, Any, Tuple, List, Optional
from sqlalchemy.orm import Session

from app.apis.evolution import send_message
from app.core.distributed_lock import DistributedLock
from app.core.logger_config import get_logger
from app.database.repositories import IARepository, LeadRepository
from app.database.models import IA, Lead
from app.schemas.webhook import WebhookPayload
from app.service.llm_response import IAresponse
from app.service.quebra_mensagem import quebrar_mensagens, calculate_typing_delay
from app.service.sanitize import sanitize_dict

log = get_logger()


class WebhookProcessor:
    """
    Processa webhooks do Evolution API seguindo princípios SOLID.

    Responsabilidades:
    - Extrair conteúdo de mensagens
    - Gerenciar leads
    - Gerar respostas da IA
    - Enviar respostas ao lead
    """

    def __init__(
        self,
        db: Session,
        ia_repository: IARepository,
        lead_repository: LeadRepository
    ):
        """
        Inicializa o processor com repositories injetados.

        Args:
            db: Sessão do banco de dados
            ia_repository: Repository para operações com IA
            lead_repository: Repository para operações com Lead
        """
        self.db = db
        self.ia_repo = ia_repository
        self.lead_repo = lead_repository

    def process(self, data: Dict[str, Any]) -> None:
        """
        Processa o payload do webhook.

        Args:
            data: Payload do webhook do Evolution API

        Raises:
            Exception: Em caso de erro no processamento
        """
        log.info("📩 Webhook recebido do Evolution")
        log.debug(json.dumps(data, indent=2, ensure_ascii=False, default=str))

        try:
            # 1️⃣ Sanitizar e validar
            data = sanitize_dict(data)
            payload = WebhookPayload(**data)

            # 2️⃣ Buscar IA
            ia_phone = payload.sender.split("@")[0]
            ia = self._get_and_validate_ia(ia_phone)

            # 3️⃣ Extrair mensagem
            message_text = self._extract_message_content(
                payload.data.model_dump(),
                payload.instance,
                payload.data.key.id,
                payload.data.messageType,
                ia
            )

            if not message_text:
                raise ValueError(
                    f"Conteúdo da mensagem não reconhecido: "
                    f"{payload.data.messageType}"
                )

            # 4️⃣ Extrair dados do lead
            lead_name = payload.data.pushName or "Usuário"
            lead_phone = payload.data.key.remoteJid.split("@")[0]

            log.info(f"👤 Lead: {lead_name} ({lead_phone})")
            log.info(f"💬 Mensagem recebida: {message_text}")

            # 5️⃣ Processar com lock distribuído
            lock_key = f"webhook_processing:{lead_phone}"
            with DistributedLock(lock_key, timeout=30):
                self._process_with_lock(
                    ia=ia,
                    instance=payload.instance,
                    lead_phone=lead_phone,
                    lead_name=lead_name,
                    message_text=message_text
                )

            log.success("✅ Webhook processado com sucesso")

        except Exception as ex:
            log.error(f"❌ Erro no processamento do webhook: {ex}", exc_info=True)
            raise

    def _get_and_validate_ia(self, ia_phone: str) -> IA:
        """
        Busca e valida a IA.

        Args:
            ia_phone: Número de telefone da IA

        Returns:
            IA: Objeto IA validado

        Raises:
            ValueError: Se IA não encontrada ou inativa
        """
        ia = self.ia_repo.get_by_phone(ia_phone)

        if not ia:
            raise ValueError("IA não encontrada")

        if not ia.status:
            raise ValueError(f"IA {ia.name} está inativa")

        return ia

    def _extract_message_content(
        self,
        data: Dict[str, Any],
        instance: str,
        message_id: str,
        message_type: str,
        ia: IA
    ) -> str:
        """
        Extrai o conteúdo da mensagem baseado no tipo.

        Args:
            data: Dados da mensagem
            instance: Instância do Evolution
            message_id: ID da mensagem
            message_type: Tipo da mensagem
            ia: Objeto IA

        Returns:
            str: Texto extraído da mensagem
        """
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

    def _process_with_lock(
        self,
        ia: IA,
        instance: str,
        lead_phone: str,
        lead_name: str,
        message_text: str
    ) -> None:
        """
        Processa a mensagem dentro da seção crítica (com lock).

        Args:
            ia: Objeto IA
            instance: Instância do Evolution
            lead_phone: Telefone do lead
            lead_name: Nome do lead
            message_text: Texto da mensagem
        """
        # 1. Gerenciar lead
        lead = self._get_or_create_lead(
            ia=ia,
            phone=lead_phone,
            name=lead_name,
            message_text=message_text
        )

        # 2. Gerar resposta da IA
        resposta_ia, historico = self._generate_ia_response(
            ia=ia,
            message_text=message_text,
            history=lead.message,
            resume=lead.resume
        )

        # 3. Enviar resposta
        self._send_response(instance, lead_phone, resposta_ia)

        # 4. Gerar resumo se necessário
        total_interacoes = self._count_interactions(historico)
        log.info(f"📊 Total de interações: {total_interacoes}")

        resumo = self._generate_resume_if_needed(
            total_interacoes=total_interacoes,
            historico=historico,
            ia=ia
        )

        # 5. Atualizar lead
        self._update_lead_with_response(lead, resposta_ia, resumo)

        # 6. Commit da transação
        self.db.commit()

        log.success(f"✅ Lead {lead.name} processado com sucesso")

    def _get_or_create_lead(
        self,
        ia: IA,
        phone: str,
        name: str,
        message_text: str
    ) -> Lead:
        """
        Busca ou cria um lead e adiciona a mensagem atual.

        Args:
            ia: Objeto IA
            phone: Telefone do lead
            name: Nome do lead
            message_text: Texto da mensagem

        Returns:
            Lead: Objeto Lead (existente ou novo)
        """
        mensagem_atual = {
            "role": "user",
            "name": name,
            "content": message_text,
        }

        lead = self.lead_repo.get_by_phone(phone)

        if lead:
            # Lead existente: adicionar mensagem ao histórico
            self.lead_repo.add_message(lead, mensagem_atual)
        else:
            # Novo lead: criar com primeira mensagem
            lead = self.lead_repo.create(
                ia_id=ia.id,
                phone=phone,
                name=name,
                message=[mensagem_atual]
            )
            log.info(f"🆕 Novo lead criado: {name} ({phone})")

        return lead

    def _generate_ia_response(
        self,
        ia: IA,
        message_text: str,
        history: List[Dict[str, Any]],
        resume: Optional[str]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Gera resposta da IA.

        Args:
            ia: Objeto IA
            message_text: Texto da mensagem do usuário
            history: Histórico de mensagens
            resume: Resumo da conversa (opcional)

        Returns:
            Tuple[str, List]: (resposta da IA, histórico)

        Raises:
            ValueError: Se não houver prompt ativo ou resposta vazia
        """
        api_key = ia.ia_config.credentials.get("api_key")
        ia_model = ia.ia_config.credentials.get("ia_model", "")
        system_prompt = ia.active_prompts

        if not system_prompt:
            raise ValueError("Nenhum prompt ativo configurado")

        llm = IAresponse(api_key, ia_model, system_prompt.prompt_text, resume)
        resposta = llm.generate_response(message_text, history)

        if not resposta:
            raise ValueError("IA não gerou resposta")

        return resposta, history

    def _send_response(self, instance: str, phone: str, resposta: str) -> None:
        """
        Envia a resposta, quebrando em múltiplas mensagens se necessário.

        Args:
            instance: Instância do Evolution
            phone: Telefone do lead
            resposta: Resposta a ser enviada
        """
        mensagens = quebrar_mensagens(resposta) or [resposta]

        for msg in mensagens:
            delay = calculate_typing_delay(msg)
            log.info(f"⏱ Delay: {delay}s")
            log.info(f"💬 Enviando: {msg}")
            send_message(instance, phone, msg, delay)

    def _count_interactions(self, historico: List[Dict[str, Any]]) -> int:
        """
        Conta alternância entre user/assistant.

        Args:
            historico: Lista de mensagens

        Returns:
            int: Número de interações
        """
        total = 0
        ultimo = None

        for msg in historico:
            if msg["role"] != ultimo:
                total += 1
                ultimo = msg["role"]

        return total

    def _generate_resume_if_needed(
        self,
        total_interacoes: int,
        historico: List[Dict[str, Any]],
        ia: IA
    ) -> Optional[str]:
        """
        Gera resumo se o número de interações atingiu um múltiplo de 20-25.

        Args:
            total_interacoes: Total de interações
            historico: Histórico de mensagens
            ia: Objeto IA

        Returns:
            Optional[str]: Resumo gerado ou None
        """
        # Gera resumo a cada 20-25 interações
        for n in range(20, 26):
            if total_interacoes % n == 0:
                log.info(f"🧠 Gerando resumo (interações={total_interacoes})")

                llm = IAresponse(
                    ia.ia_config.credentials.get("api_key"),
                    ia.ia_config.credentials.get("ia_model"),
                    ia.active_prompts.prompt_text,
                    None,
                )

                return llm.generate_resume(historico)

        return None

    def _update_lead_with_response(
        self,
        lead: Lead,
        resposta: str,
        resumo: Optional[str]
    ) -> None:
        """
        Atualiza o lead com a resposta da IA e resumo.

        Args:
            lead: Objeto Lead
            resposta: Resposta da IA
            resumo: Resumo da conversa (opcional)
        """
        response_message = {
            "role": "assistant",
            "content": resposta,
        }

        self.lead_repo.update_with_response(lead, response_message, resumo)


# ===============================================================
#  🔹 FUNÇÃO LEGACY (mantida para compatibilidade)
# ===============================================================
def process_webhook_data(data: Dict[str, Any]) -> None:
    """
    Função legacy para processar webhook.

    DEPRECATED: Use WebhookProcessor diretamente.

    Args:
        data: Payload do webhook
    """
    from app.database.connection import SessionLocal

    db = SessionLocal()
    try:
        ia_repo = IARepository(db)
        lead_repo = LeadRepository(db)

        processor = WebhookProcessor(db, ia_repo, lead_repo)
        processor.process(data)

        db.commit()
    except Exception as ex:
        db.rollback()
        log.error(f"Erro ao processar webhook: {ex}", exc_info=True)
        raise
    finally:
        db.close()
