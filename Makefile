ifeq ($(OS),Windows_NT)
    VENV_BIN = venv\Scripts
    SEP = \\
    ACTIVATE_CMD = $(VENV_BIN)\activate.bat &&
    RM_CMD = rmdir /s /q
    MKDIR_CMD = mkdir
    VENV_PYTHON = venv\Scripts\python.exe
else
    VENV_BIN = venv/bin
    SEP = /
    ACTIVATE_CMD = . $(VENV_BIN)/activate &&
    RM_CMD = rm -rf
    MKDIR_CMD = mkdir -p
    VENV_PYTHON = venv/bin/python
endif

INSTALL_CMD = pip install -r src/requirements.txt
PYTHON = poetry run python

AWS_REGION ?= us-east-1
ENVIRONMENT ?= dev
TFVARS_PATH ?= ./envs/$(ENVIRONMENT)/terraform.tfvars
REPOSITORY_OWNER := $(shell git remote get-url origin | sed -n 's/.*[:/]\([^/]*\)\/[^/]*\.git/\1/p')

REPO_NAME := $(shell basename `git rev-parse --show-toplevel`)
REPO_CREATION_DATE := $(shell git log --reverse --format=%aI | head -n 1)
REPO_CREATOR := $(shell git log --reverse --format='%aN' | head -n 1)

BACKEND_BUCKET := $(AWS_REGION)-$(REPOSITORY_OWNER)--tfstates
BACKEND_KEY := $(REPO_NAME)
DYNAMODB_TABLE := $(REPOSITORY_OWNER)-$(AWS_REGION)-terraform-lock

TF_COMMON_VARS := -var "creation_date=$(REPO_CREATION_DATE)" \
                 -var "author=$(REPO_CREATOR)" \
                 -var "TagProject=$(REPO_NAME)" \
                 -var "TagEnv=$(ENVIRONMENT)" \
                 -var "aws_region=$(AWS_REGION)" \
                 -var-file="$(TFVARS_PATH)"

.PHONY: help \
        install venv-check venv-create run setup-chrome \
        install-p lint format test coverage clean docs pre-test all \
        init validate workspace plan apply deploy destroy tf-test empty-s3-ecr plan-apply

.DEFAULT_GOAL := help

##############################
# Seção: Ambiente Virtual Python
##############################

install: venv-check

install-full: install setup-chrome

venv-check: src/requirements.txt
	@if [ ! -f $(VENV_PYTHON) ]; then \
		echo ">>> [Make] Ambiente virtual não encontrado, criando..."; \
		$(MAKE) venv-create; \
	else \
		echo ">>> [Make] Ambiente virtual encontrado, verificando atualizações..."; \
		$(ACTIVATE_CMD) pip install --upgrade pip setuptools wheel && $(INSTALL_CMD); \
	fi

venv-create:
	$(RM_CMD) venv 2>/dev/null || true
	python -m venv venv
	$(ACTIVATE_CMD) pip install --upgrade pip setuptools wheel && $(INSTALL_CMD)
	@echo ">>> [Make] Ambiente virtual criado e dependências instaladas."
	@echo "Para ativar o ambiente virtual:"
ifeq ($(OS),Windows_NT)
	@echo "    $(VENV_BIN)\activate.bat"
else
	@echo "    source $(VENV_BIN)/activate"
endif

setup-chrome:
	@echo ">>> [Make] Configurando Chrome para automação..."
	chmod +x src/setup.sh
	sudo ./src/setup.sh -y

run:
	@echo ">>> [Make] Executando aplicação principal..."
	$(ACTIVATE_CMD) python ./src/main.py

##############################
# Seção: Tarefas Poetry
##############################

install-p:
	@echo ">>> [Make] Instalando dependências via Poetry..."
	poetry install

lint:
	@echo ">>> [Make] Executando verificação de código com Ruff..."
	poetry run ruff check .
	poetry run ruff check --fix .

format:
	@echo ">>> [Make] Formatando código com isort e black..."
	poetry run isort .
	poetry run black .

test:
	@echo ">>> [Make] Executando testes com relatório de cobertura..."
	poetry run pytest -s -x --cov=src --cov-report=term-missing

coverage:
	@echo ">>> [Make] Gerando relatório de cobertura HTML..."
	poetry run pytest --cov=src --cov-report=html

docs:
	@echo ">>> [Make] Gerando documentação com Sphinx..."
	cd docs && sphinx-build -b html . _build/html

pre-test: lint

all: install-p format lint test

##############################
# Seção: Terraform
##############################
tf-fmt:
	@echo ">>> [Make] Formatando arquivos Terraform..."
	cd infra && terraform fmt -recursive

tf-fmt-check:
	@echo ">>> [Make] Verificando formatação dos arquivos Terraform..."
	cd infra && terraform fmt -check -recursive

fmt: tf-fmt tf-fmt-check

init:
	@echo ">>> [Make] Inicializando Terraform..."
	cd infra && terraform init \
	  -backend-config="bucket=$(BACKEND_BUCKET)" \
	  -backend-config="key=$(BACKEND_KEY)" \
	  -backend-config="region=$(AWS_REGION)" \
	  -backend-config="dynamodb_table=$(DYNAMODB_TABLE)"

validate: tf-fmt-check tf-fmt
	@echo ">>> [Make] Validando configuração do Terraform..."
	cd infra && terraform validate

workspace:
	@echo ">>> [Make] Selecionando/criando workspace $(ENVIRONMENT)..."
	cd infra && (terraform workspace select $(ENVIRONMENT) || terraform workspace new $(ENVIRONMENT))

plan:
	@echo ">>> [Make] Criando plano do Terraform..."
	cd infra && terraform plan $(TF_COMMON_VARS) -out="$(ENVIRONMENT).plan"

apply:
	@echo ">>> [Make] Aplicando alterações do Terraform..."
	cd infra && terraform apply "$(ENVIRONMENT).plan"
	@echo ">>> [Make] Terraform deployment concluído com sucesso!"


tf-test:
	@echo ">>> [Make] Rodando terraform test..."
	cd infra && terraform test

empty-s3-ecr:
	@echo ">>> [Make] Esvaziando buckets S3 e repositórios ECR para o ambiente: $(ENVIRONMENT)"
	chmod +x ./.github/deploy/empty_s3_ecr.sh
	./.github/deploy/empty_s3_ecr.sh "$(ENVIRONMENT)"

destroy:
	@echo ">>> [Make] Destruindo infraestrutura..."
	cd infra && terraform workspace select $(ENVIRONMENT) && \
	terraform destroy $(TF_COMMON_VARS) -auto-approve

deploy: fmt init validate tf-test workspace plan apply

##############################
# Seção: Limpeza
##############################

clean:
	@echo ">>> [Make] Removendo arquivos temporários e ambientes..."
	$(RM_CMD) venv 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage coverage.xml htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	cd infra && rm -f *.plan
	@echo ">>> [Make] Limpeza concluída."


##############################
# Seção: Ajuda
##############################

help:
	@echo "====================== MAKEFILE HELP ======================"
	@echo ""
	@echo "COMANDOS GERAIS:"
	@echo "  help              - Exibe esta mensagem de ajuda"
	@echo "  clean             - Remove ambientes virtuais e arquivos temporários"
	@echo ""
	@echo "AMBIENTE PYTHON:"
	@echo "  install           - Cria ambiente virtual e instala dependências"
	@echo "  venv-check        - Verifica se o ambiente virtual existe e está atualizado"
	@echo "  venv-create       - Cria um novo ambiente virtual"
	@echo "  run               - Executa a aplicação principal no ambiente virtual"
	@echo "  setup-chrome      - Configura o Chrome para automação"
	@echo ""
	@echo "DESENVOLVIMENTO (POETRY):"
	@echo "  install-p         - Instala dependências usando Poetry"
	@echo "  lint              - Executa verificação de código com Ruff"
	@echo "  format            - Formata código usando isort e black"
	@echo "  test              - Executa testes com relatório de cobertura"
	@echo "  coverage          - Gera relatório de cobertura HTML"
	@echo "  docs              - Gera documentação com Sphinx"
	@echo "  pre-test          - Executa lint antes dos testes"
	@echo "  all               - Fluxo completo: instala, formata, verifica e testa"
	@echo ""
	@echo "TERRAFORM:"
	@echo "  tf-fmt            - Formata arquivos Terraform"
	@echo "  tf-fmt-check      - Verifica formatação dos arquivos Terraform"
	@echo "  fmt               - Executa formatação e verificação dos arquivos Terraform"
	@echo "  init              - Inicializa o Terraform"
	@echo "  validate          - Valida a configuração do Terraform (após formatação)"
	@echo "  workspace         - Seleciona ou cria o workspace Terraform"
	@echo "  plan              - Gera o plano de execução do Terraform"
	@echo "  apply             - Aplica o plano gerado pelo Terraform"
	@echo "  deploy            - Fluxo completo: fmt, init, validate, workspace, plan, apply"
	@echo "  destroy           - Destrói a infraestrutura"
	@echo "  tf-test           - Executa testes do Terraform"
	@echo "  empty-s3-ecr      - Esvazia buckets S3 e repositórios ECR"
	@echo ""
	@echo "VARIÁVEIS:"
	@echo "  ENVIRONMENT       - Ambiente (padrão: dev)"
	@echo "  AWS_REGION        - Região AWS (padrão: us-east-1)"
	@echo "  REPOSITORY_OWNER  - Proprietário do repositório (extraído automaticamente do Git)"
	@echo "  TFVARS_PATH       - Caminho para o arquivo tfvars"
	@echo "=========================================================="