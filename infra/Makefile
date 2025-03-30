AWS_REGION ?= us-east-1
ENVIRONMENT ?= dev
TFVARS_PATH ?= ./envs/$(ENVIRONMENT)/terraform.tfvars
REPOSITORY_OWNER ?= trababalhos-puc
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

.PHONY: all init validate workspace plan apply destroy clean help

all: init validate workspace plan apply

deploy: workspace plan apply

init:
	@echo "Inicializando Terraform..."
	terraform init \
	  -backend-config="bucket=$(BACKEND_BUCKET)" \
	  -backend-config="key=$(BACKEND_KEY)" \
	  -backend-config="region=$(AWS_REGION)" \
	  -backend-config="dynamodb_table=$(DYNAMODB_TABLE)"

validate:
	@echo "Validando configuração do Terraform..."
	terraform validate

workspace:
	@echo "Selecionando/criando workspace $(ENVIRONMENT)..."
	terraform workspace select $(ENVIRONMENT) || terraform workspace new $(ENVIRONMENT)

plan:
	@echo "Criando plano do Terraform..."
	terraform plan $(TF_COMMON_VARS) -out="$(ENVIRONMENT).plan"

apply:
	@echo "Aplicando alterações do Terraform..."
	terraform apply "$(ENVIRONMENT).plan"
	@echo "Terraform deployment completed successfully!"

destroy:
	@echo "Destruindo infraestrutura..."
	terraform destroy $(TF_COMMON_VARS) -auto-approve

clean:
	@echo "Limpando arquivos temporários..."
	rm -f *.plan
	rm -rf .terraform/

help:
	@echo "Makefile para gerenciar operações do Terraform"
	@echo ""
	@echo "Targets disponíveis:"
	@echo "  all       : Executa init, validate, workspace, plan e apply"
	@echo "  init      : Inicializa o backend do Terraform"
	@echo "  validate  : Valida os arquivos do Terraform"
	@echo "  workspace : Seleciona ou cria o workspace"
	@echo "  plan      : Gera o plano de execução"
	@echo "  apply     : Aplica o plano gerado"
	@echo "  destroy   : Destrói a infraestrutura"
	@echo "  clean     : Remove arquivos temporários"
	@echo ""
	@echo "Variáveis:"
	@echo "  AWS_REGION       : Região da AWS (default: us-east-1)"
	@echo "  ENVIRONMENT      : Ambiente (default: dev)"
	@echo "  TFVARS_PATH      : Caminho para o arquivo tfvars"
	@echo "  REPOSITORY_OWNER : Dono do repositório"