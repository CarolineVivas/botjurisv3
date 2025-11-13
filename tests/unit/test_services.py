# tests/unit/test_services.py

import pytest

from app.service.process import process_webhook_data


@pytest.mark.unit
def test_process_webhook_data_text_message(monkeypatch):
    """
    Testa o fluxo principal do process_webhook_data com mensagem de texto simples.
    Tudo que toca banco, IA ou Evolution é mockado.
    """

    # Payload bruto simulando o enviado pelo Evolution
    payload = {
        "instance": "minha-instancia-1",
        "sender": "5511999999999@wa.me",
        "data": {
            "key": {
                "id": "MSG123",
                "remoteJid": "5511999999999@wa.me",
            },
            "messageType": "conversation",
            "message": {
                "conversation": "Olá, tudo bem?",
            },
            "pushName": "Caroline",
        },
    }

    # ---- mocks ----

    class FakeIAConfig:
        def __init__(self):
            self.credentials = {"api_key": "fake-key", "ia_model": "gpt-fake"}

    class FakePrompt:
        def __init__(self):
            self.prompt_text = "Você é um assistente de testes."

    class FakeIAInfos:
        def __init__(self):
            self.id = 1
            self.status = True
            self.nome = "IA Teste"
            self.ia_config = FakeIAConfig()
            self.active_prompts = FakePrompt()

    class FakeLead:
        def __init__(self):
            self.id = 123
            self.name = "Caroline"
            self.message = []
            self.resume = None

    # ia_manipulations.filter_ia -> retorna uma IA fake
    def fake_filter_ia(phone):
        return FakeIAInfos()

    # lead_manipulations.filter_lead -> retorna None pra simular lead novo
    def fake_filter_lead(phone, message_atual_lead):
        return None

    # lead_manipulations.new_lead -> retorna FakeLead
    def fake_new_lead(ia_id, phone, name, historico):
        lead = FakeLead()
        lead.message = historico
        return lead

    # IAresponse.generate_response -> responde sempre a mesma string
    class FakeIAResponse:
        def __init__(self, api_key, model, system_prompt, resume):
            self.api_key = api_key
            self.model = model
            self.system_prompt = system_prompt
            self.resume = resume

        def generate_response(self, message, historico):
            return "Resposta gerada pela IA de teste."

        def generate_resume(self, historico):
            return "Resumo de teste."

    # quebra_mensagens -> retorna lista com uma mensagem
    def fake_quebrar_mensagens(msg):
        return [msg]

    # calculate_typing_delay -> delay fixo
    def fake_calculate_typing_delay(msg):
        return 0

    sent_messages = []

    def fake_send_message(instance_name, phone, message, delay):
        sent_messages.append(
            {
                "instance": instance_name,
                "phone": phone,
                "message": message,
                "delay": delay,
            }
        )

    # ---- aplica monkeypatch ----
    from app import service as app_service  # type: ignore

    monkeypatch.setattr("app.database.manipulations.ia_manipulations.filter_ia", fake_filter_ia)
    monkeypatch.setattr("app.database.manipulations.lead_manipulations.filter_lead", fake_filter_lead)
    monkeypatch.setattr("app.database.manipulations.lead_manipulations.new_lead", fake_new_lead)
    monkeypatch.setattr("app.service.llm_response.IAresponse", FakeIAResponse)
    monkeypatch.setattr("app.service.quebra_mensagem.quebrar_mensagens", fake_quebrar_mensagens)
    monkeypatch.setattr("app.service.quebra_mensagem.calculate_typing_delay", fake_calculate_typing_delay)
    monkeypatch.setattr("app.apis.evolution.send_message", fake_send_message)

    # ---- chama função ----
    process_webhook_data(payload)

    # ---- valida ----
    assert len(sent_messages) == 1
    msg = sent_messages[0]
    assert msg["instance"] == "minha-instancia-1"
    assert msg["phone"] == "5511999999999"
    assert "Resposta gerada" in msg["message"]
