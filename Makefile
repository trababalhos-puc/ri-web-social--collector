##############################
# Seção: Tarefas Python (Poetry)
##############################

PYTHON = poetry run python

.PHONY: install lint format test coverage clean pre-test all

install:
	poetry install

lint:
	poetry run ruff check .
	poetry run ruff check --fix .

format:
	poetry run isort .
	poetry run black .

test:
	poetry run pytest -s -x --cov=src --cov-report=term-missing

coverage:
	poetry run pytest --cov=src --cov-report=html

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage coverage.xml htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	cd docs && sphinx-build -b html . _build/html

pre-test: lint

all: install format lint test

##############################
# Seção: Tarefas Terraform / CI-CD
##############################

.PHONY: init validate empty-s3-ecr destroy plan-apply plan apply help

ENVIRONMENT ?= dev
AWS_ACCOUNT ?= 123456789012
AWS_REGION ?= us-east-1
PROJECT_NAME ?= meu-projeto
REPO_OWNER ?= meu-usuario


init:
	@echo ">>> [Make] Rodando terraform init..."
	chmod +x ./.github/deploy/terraform_init.sh
	./.github/deploy/terraform_init.sh "$(AWS_REGION)" "$(REPO_OWNER)" "$(PROJECT_NAME)"


validate:
	@echo ">>> [Make] Rodando terraform validate..."
	chmod +x ./.github/deploy/terraform_validate.sh
	./.github/deploy/terraform_validate.sh

tf-test:
	@echo ">>> [Make] Rodando terraform test..."
	chmod +x ./.github/deploy/terraform_test.sh
	./.github/deploy/terraform_test.sh

empty-s3-ecr:
	@echo ">>> [Make] Esvaziando buckets S3 e repositórios ECR para o ambiente: $(ENVIRONMENT)"
	chmod +x ./.github/deploy/empty_s3_ecr.sh
	./.github/deploy/empty_s3_ecr.sh "$(ENVIRONMENT)"

destroy:
	@echo ">>> [Make] Executando terraform destroy para o ambiente: $(ENVIRONMENT)"
	chmod +x ./.github/deploy/terraform_destroy.sh
	./.github/deploy/terraform_destroy.sh "$(ENVIRONMENT)"

plan-apply:
	@echo ">>> [Make] Executando terraform plan e apply para o ambiente: $(ENVIRONMENT)"
	chmod +x ./.github/deploy/terraform_plan_apply.sh
	./.github/deploy/terraform_plan_apply.sh "$(ENVIRONMENT)"

help:
	@echo "Lista de comandos disponíveis:"
	@echo "  [Python]"
	@echo "    install, lint, format, test, coverage, clean, pre-test, all"
	@echo "  [Terraform]"
	@echo "    init, validate, empty-s3-ecr, destroy, plan-apply, help"
