# tests/unit/test_sanitize.py
import pytest
from app.service.sanitize import sanitize_text, sanitize_dict


class TestSanitizeText:
    """Testes para limpeza de texto"""
    
    def test_remove_control_characters(self):
        """Remove caracteres de controle invisíveis"""
        texto = "Olá\x00mundo\x08test"
        resultado = sanitize_text(texto)
        assert "\x00" not in resultado
        assert "\x08" not in resultado
        assert "Olámundotest" in resultado
    
    def test_normalize_whitespace(self):
        """Normaliza espaços múltiplos"""
        texto = "Olá    mundo   teste"
        resultado = sanitize_text(texto)
        assert resultado == "Olá mundo teste"
    
    def test_trim_edges(self):
        """Remove espaços nas extremidades"""
        texto = "  Olá mundo  "
        resultado = sanitize_text(texto)
        assert resultado == "Olá mundo"
    
    def test_limit_length(self):
        """Limita tamanho máximo"""
        texto = "a" * 5000
        resultado = sanitize_text(texto, max_len=100)
        assert len(resultado) == 100
    
    def test_normalize_accents(self):
        """Mantém acentuação normalizada"""
        texto = "Ação, café, José"
        resultado = sanitize_text(texto)
        assert "Ação" in resultado
        assert "café" in resultado
        assert "José" in resultado
    
    def test_empty_string(self):
        """Retorna string vazia para entrada vazia"""
        assert sanitize_text("") == ""
        assert sanitize_text(None) == ""


class TestSanitizeDict:
    """Testes para limpeza de dicionários"""
    
    def test_sanitize_string_values(self):
        """Limpa valores string em dicionário"""
        data = {
            "nome": "  João  ",
            "mensagem": "Olá   mundo"
        }
        resultado = sanitize_dict(data)
        assert resultado["nome"] == "João"
        assert resultado["mensagem"] == "Olá mundo"
    
    def test_nested_dict(self):
        """Limpa dicionários aninhados"""
        data = {
            "user": {
                "name": "  Maria  ",
                "message": "  Teste  "
            }
        }
        resultado = sanitize_dict(data)
        assert resultado["user"]["name"] == "Maria"
        assert resultado["user"]["message"] == "Teste"
    
    def test_list_of_strings(self):
        """Limpa listas de strings"""
        data = {
            "tags": ["  python  ", "  fastapi  "]
        }
        resultado = sanitize_dict(data)
        assert resultado["tags"] == ["python", "fastapi"]
    
    def test_non_string_values_unchanged(self):
        """Mantém valores não-string inalterados"""
        data = {
            "count": 42,
            "active": True,
            "score": 9.8
        }
        resultado = sanitize_dict(data)
        assert resultado["count"] == 42
        assert resultado["active"] is True
        assert resultado["score"] == 9.8
    
    def test_xss_prevention(self):
        """Não executa scripts, apenas limpa texto"""
        data = {
            "input": "<script>alert('xss')</script>"
        }
        resultado = sanitize_dict(data)
        # sanitize_text não remove HTML, só caracteres de controle
        # Para remover HTML, você precisaria de bleach ou similar
        assert "<script>" in resultado["input"]  # comportamento atual
