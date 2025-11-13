# tests/unit/test_cache_service.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.service.cache_service import (
    set_cache,
    get_cache,
    delete_cache,
    cache_prompt,
    get_cached_prompt,
    cache_ia_config,
    get_cached_ia_config,
    cache_lead_session,
    get_lead_session,
)


@pytest.fixture
def mock_redis():
    """Fixture que mocka o cliente Redis"""
    with patch("app.service.cache_service.redis_client") as mock:
        mock.setex = Mock()
        mock.get = Mock()
        mock.delete = Mock()
        yield mock


class TestCacheBasicOperations:
    """Testes para operações básicas de cache"""
    
    def test_set_cache_success(self, mock_redis):
        """Armazena valor no cache com sucesso"""
        mock_redis.setex.return_value = True
        
        set_cache("test_key", {"data": "value"}, expire_seconds=60)
        
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == "test_key"
        assert args[1] == 60
        # args[2] seria o JSON serializado
    
    def test_get_cache_success(self, mock_redis):
        """Recupera valor do cache"""
        import json
        mock_redis.get.return_value = json.dumps({"data": "value"})
        
        result = get_cache("test_key")
        
        assert result == {"data": "value"}
        mock_redis.get.assert_called_once_with("test_key")
    
    def test_get_cache_not_found(self, mock_redis):
        """Retorna None quando chave não existe"""
        mock_redis.get.return_value = None
        
        result = get_cache("nonexistent")
        
        assert result is None
    
    def test_delete_cache_success(self, mock_redis):
        """Remove chave do cache"""
        mock_redis.delete.return_value = 1
        
        delete_cache("test_key")
        
        mock_redis.delete.assert_called_once_with("test_key")
    
    def test_cache_handles_redis_unavailable(self, mock_redis):
        """Não quebra quando Redis está indisponível"""
        mock_redis.setex.side_effect = Exception("Redis down")
        
        # Não deve lançar exceção
        set_cache("test_key", {"data": "value"})


class TestPromptCache:
    """Testes para cache de prompts"""
    
    def test_cache_prompt(self, mock_redis):
        """Armazena prompt no cache"""
        prompt_data = {
            "id": 1,
            "text": "Você é um assistente",
            "is_active": True
        }
        
        cache_prompt("1", prompt_data, ttl=3600)
        
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == "prompt:1"
        assert args[1] == 3600
    
    def test_get_cached_prompt(self, mock_redis):
        """Recupera prompt do cache"""
        import json
        mock_redis.get.return_value = json.dumps({"text": "Prompt"})
        
        result = get_cached_prompt("1")
        
        assert result == {"text": "Prompt"}
        mock_redis.get.assert_called_once_with("prompt:1")


class TestIAConfigCache:
    """Testes para cache de configuração da IA"""
    
    def test_cache_ia_config(self, mock_redis):
        """Armazena config da IA"""
        config = {
            "model": "gpt-4o-mini",
            "temperature": 0.7
        }
        
        cache_ia_config(config, ttl=7200)
        
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == "ia:config"
        assert args[1] == 7200
    
    def test_get_cached_ia_config(self, mock_redis):
        """Recupera config da IA"""
        import json
        mock_redis.get.return_value = json.dumps({"model": "gpt-4o-mini"})
        
        result = get_cached_ia_config()
        
        assert result["model"] == "gpt-4o-mini"


class TestLeadSessionCache:
    """Testes para cache de sessão de leads"""
    
    def test_cache_lead_session(self, mock_redis):
        """Armazena sessão do lead"""
        session_data = {
            "id": "123",
            "name": "Caroline",
            "messages": []
        }
        
        cache_lead_session("123", session_data, ttl=1800)
        
        mock_redis.setex.assert_called_once()
        args = mock_redis.setex.call_args[0]
        assert args[0] == "lead_session:123"
        assert args[1] == 1800
    
    def test_get_lead_session(self, mock_redis):
        """Recupera sessão do lead"""
        import json
        mock_redis.get.return_value = json.dumps({"name": "Caroline"})
        
        result = get_lead_session("123")
        
        assert result["name"] == "Caroline"
        mock_redis.get.assert_called_once_with("lead_session:123")