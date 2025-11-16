# tests/unit/test_crypto.py
"""
Testes unitários para o módulo de criptografia.
"""
import pytest

from app.service.crypto import decrypt_data, encrypt_data


class TestCryptography:
    """Testes para funções de criptografia"""

    def test_encrypt_and_decrypt_string(self):
        """Testa criptografia e descriptografia de string"""
        original = "Dados sensíveis do usuário"

        encrypted = encrypt_data(original)
        decrypted = decrypt_data(encrypted)

        assert encrypted != original  # Deve estar criptografado
        assert decrypted == original  # Deve voltar ao original

    def test_encrypt_returns_different_values(self):
        """Testa que mesma entrada gera saídas diferentes (por causa do IV)"""
        data = "Teste de segurança"

        encrypted1 = encrypt_data(data)
        encrypted2 = encrypt_data(data)

        # Devem ser diferentes (mesmo com mesma entrada)
        assert encrypted1 != encrypted2

        # Mas ambos devem descriptografar para o valor original
        assert decrypt_data(encrypted1) == data
        assert decrypt_data(encrypted2) == data

    def test_encrypt_empty_string(self):
        """Testa criptografia de string vazia"""
        encrypted = encrypt_data("")
        decrypted = decrypt_data(encrypted)

        assert decrypted == ""

    def test_encrypt_with_special_characters(self):
        """Testa criptografia com caracteres especiais"""
        original = "Olá! @#$% 123 🎉"

        encrypted = encrypt_data(original)
        decrypted = decrypt_data(encrypted)

        assert decrypted == original

    def test_encrypt_large_text(self):
        """Testa criptografia de texto grande"""
        original = "A" * 10000  # 10KB de texto

        encrypted = encrypt_data(original)
        decrypted = decrypt_data(encrypted)

        assert decrypted == original

    def test_decrypt_invalid_data_raises_error(self):
        """Testa que dados inválidos geram erro na descriptografia"""
        with pytest.raises(Exception):
            decrypt_data("dados_invalidos_123")

    def test_encrypt_unicode(self):
        """Testa criptografia com caracteres unicode"""
        original = "Português: ção, José. 中文: 你好. Emoji: 😀🎉"

        encrypted = encrypt_data(original)
        decrypted = decrypt_data(encrypted)

        assert decrypted == original

    def test_encrypt_json_string(self):
        """Testa criptografia de string JSON"""
        original = '{"nome": "Caroline", "idade": 30, "ativo": true}'

        encrypted = encrypt_data(original)
        decrypted = decrypt_data(encrypted)

        assert decrypted == original
