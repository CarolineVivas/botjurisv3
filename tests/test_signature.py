import hmac
import hashlib
import json
import requests

# Deve ser a MESMA chave usada no backend (.env ou config)
WEBHOOK_SECRET = "chave_super_segura_gerada_no_painel"

payload = {
    "instance": "BotJuris",
    "sender": "557996533036@s.whatsapp.net",
    "data": {
        "key": {
            "id": "ABC123XYZ987",
            "remoteJid": "5584998765432@s.whatsapp.net",
            "fromMe": False
        },
        "message": {
            "conversation": "Olá, quero saber sobre meus direitos trabalhistas."
        },
        "messageType": "conversation",
        "pushName": "Caroline"
    }
}

body = json.dumps(payload).encode()
signature = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()

resp = requests.post(
    "http://127.0.0.1:8080/webhook",
    headers={
        "Content-Type": "application/json",
        "X-Signature": signature
    },
    data=body
)

print(resp.status_code, resp.text)

