# tests/unit/test_config.py
"""
Testes unitários para o módulo de configuração.
"""
from app.core.config import Settings, get_settings


class TestSettings:
    """Testes para a classe Settings"""

    def test_settings_with_valid_data(self, mock_settings):
        """Testa criação de Settings com dados válidos"""
        assert mock_settings.APP_NAME == "BotJuris Test"
        assert mock_settings.ENVIRONMENT == "development"
        assert mock_settings.DEBUG is True

    def test_environment_validation(self):
        """Testa se aceita apenas ambientes válidos"""
        from cryptography.fernet import Fernet

        valid_envs = ["development", "staging", "production"]

        for env in valid_envs:
            settings = Settings(
                DATABASE_URL="postgresql://test:test@localhost/db",
                ENVIRONMENT=env,
                EVOLUTION_HOST="http://test.com/",
                EVOLUTION_API_KEY="test-key-minimum-10-chars",
                OPENAI_API_KEY="sk-test-key-with-minimum-20-characters",  # ✅ 20+ chars
                FERNET_KEY=Fernet.generate_key().decode(),  # ✅ Adicionar essa linha!
            )
            assert settings.ENVIRONMENT == env

    def test_redis_url_with_password(self, mock_settings):
        """Testa construção de URL Redis com senha"""
        mock_settings.REDIS_PASSWORD = "secret123"

        url = mock_settings.get_redis_url_with_password()

        assert "secret123" in url
        assert url.startswith("redis://:")

    def test_is_production_property(self, mock_settings):
        """Testa propriedade is_production"""
        mock_settings.ENVIRONMENT = "production"
        assert mock_settings.is_production is True

        mock_settings.ENVIRONMENT = "development"
        assert mock_settings.is_production is False

    def test_is_development_property(self, mock_settings):
        """Testa propriedade is_development"""
        mock_settings.ENVIRONMENT = "development"
        assert mock_settings.is_development is True

        mock_settings.ENVIRONMENT = "production"
        assert mock_settings.is_development is False


class TestGetSettings:
    """Testes para a função get_settings (singleton)"""

    def test_get_settings_returns_same_instance(self):
        """Testa se get_settings retorna sempre a mesma instância"""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2  # Mesma instância (singleton)

    def test_get_settings_loads_from_env(self):
        """Testa se get_settings carrega do .env"""
        settings = get_settings()

        # Deve ter carregado as variáveis do .env
        assert settings.APP_NAME is not None
        assert settings.DATABASE_URL is not None
