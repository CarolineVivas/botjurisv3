# Makefile - Comandos úteis para o projeto

.PHONY: help install test lint format clean run docker-up docker-down

# Comando padrão
help:
	@echo "📋 Comandos disponíveis:"
	@echo ""
	@echo "  make install       - Instala todas as dependências"
	@echo "  make test          - Roda todos os testes"
	@echo "  make test-unit     - Roda apenas testes unitários"
	@echo "  make test-cov      - Roda testes com coverage"
	@echo "  make lint          - Verifica código com ruff"
	@echo "  make format        - Formata código com black"
	@echo "  make format-check  - Verifica formatação sem modificar"
	@echo "  make typecheck     - Verifica tipos com mypy"
	@echo "  make clean         - Remove arquivos temporários"
	@echo "  make run           - Inicia a aplicação"
	@echo "  make run-dev       - Inicia em modo desenvolvimento"
	@echo "  make docker-up     - Inicia containers (Redis, etc)"
	@echo "  make docker-down   - Para containers"
	@echo "  make pre-commit    - Instala hooks de pre-commit"

# Instalação
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Testes
test:
	pytest

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term-missing

# Linting e Formatação
lint:
	ruff check app tests

lint-fix:
	ruff check app tests --fix

format:
	black app tests
	ruff check app tests --fix --select I

format-check:
	black app tests --check
	ruff check app tests

# Type Checking
typecheck:
	mypy app

# Limpeza
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -f .coverage

# Execução
run:
	python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

run-dev:
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Docker
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Pre-commit
pre-commit:
	pre-commit install
	pre-commit autoupdate

pre-commit-run:
	pre-commit run --all-files

# Qualidade geral (roda tudo)
quality: format lint typecheck test
	@echo "✅ Todos os checks passaram!"
