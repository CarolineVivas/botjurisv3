# tests/integration/test_webhook.py

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
@pytest.mark.api
def test_webhook_evolution_enfileira_payload(client: TestClient, monkeypatch):
    """
    Testa se a rota do webhook do Evolution responde OK
    e chama enqueue_webhook com o payload recebido.
    """
    from app.service import queue_manager

    captured = {}

    def fake_enqueue(payload):
        captured["payload"] = payload

    monkeypatch.setattr(queue_manager, "enqueue_webhook", fake_enqueue)

    payload = {
        "instance": "instancia-test",
        "sender": "5511999999999@wa.me",
        "data": {
            "key": {
                "id": "MSG123",
                "remoteJid": "5511999999999@wa.me",
            },
            "messageType": "conversation",
            "message": {"conversation": "Olá, tudo bem?"},
            "pushName": "Caroline",
        },
    }

    response = client.post("/webhook/evolution", json=payload)

    assert response.status_code in (200, 202)
    body = response.json()
    # Ajuste conforme sua rota retornar
    assert "status" in body
    captured_payload = captured.get("payload")
    assert captured_payload is not None
    assert captured_payload["instance"] == "instancia-test"
