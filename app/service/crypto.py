import os
import json
from dotenv import load_dotenv
from cryptography.fernet import Fernet, InvalidToken

# ✅ Carrega variáveis do ambiente (.env)
load_dotenv()

FERNET_KEY = os.getenv("FERNET_KEY")

if not FERNET_KEY:
    raise ValueError("⚠️ FERNET_KEY não encontrada no arquivo .env")

try:
    fernet = Fernet(FERNET_KEY.encode())
except Exception as e:
    raise ValueError(f"❌ Erro ao inicializar Fernet: {e}")

# 🔒 Encripta qualquer dicionário Python em string segura
def encrypt_data(data: dict) -> str:
    try:
        json_data = json.dumps(data)
        encrypted_data = fernet.encrypt(json_data.encode()).decode()
        return encrypted_data
    except Exception as e:
        raise ValueError(f"Erro ao criptografar dados: {e}")

# 🔓 Desencripta a string e retorna o dicionário original
def decrypt_data(encrypted_str: str) -> dict:
    try:
        decrypted_bytes = fernet.decrypt(encrypted_str.encode())
        data_json = json.loads(decrypted_bytes.decode())
        return data_json
    except InvalidToken:
        raise ValueError("❌ Token inválido ou corrompido. Verifique a chave Fernet.")
    except Exception as e:
        raise ValueError(f"Erro ao descriptografar dados: {e}")

# 🔧 Teste rápido opcional (somente se rodar standalone)
if __name__ == "__main__":
    data_encrypted = encrypt_data({"teste": "teste"})
    print("Criptografado:", data_encrypted)
    print("Decriptado:", decrypt_data(data_encrypted))
