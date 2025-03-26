# Documentação do Fluxo de Trabalho do GitHub Actions

## Visão Geral

Este projeto utiliza GitHub Actions para Integração Contínua e Implantação Contínua (CI/CD) em múltiplos ambientes.

## Gatilhos do Fluxo de Trabalho

Os fluxos de trabalho são acionados por:
- Pushes para branches `main` e `staging`
- Acionamento manual de workflow

## Determinação de Ambiente

O workflow determina dinamicamente o ambiente de implantação com base em:
- Branch sendo enviada
- Seleção manual durante o acionamento do workflow

### Mapeamento de Ambientes
- Branch `main` → Produção
- Branch `staging` → Staging
- Acionamento manual → Ambiente selecionado pelo usuário

## Jobs

### Job de Testes
- Executa no Ubuntu mais recente
- Verifica o código-fonte
- Configura Python 3.12
- Usa Poetry para gerenciamento de dependências
- Realiza:
    - Instalação de dependências
    - Verificação de código
    - Testes unitários
    - Relatório de cobertura

### Job de Segurança
- Executa varreduras de segurança
- Depende da conclusão bem-sucedida do job de testes

### Job de Implantação Terraform
- Implanta infraestrutura usando Terraform
- Suporta múltiplos ambientes (desenvolvimento, staging, produção)
- Usa credenciais AWS para implantação

## Gerenciamento de Configuração

### Ferramentas Utilizadas
- GitHub Actions
- Poetry
- Terraform
- Ruff (verificação de código)
- Pytest (testes)

## Melhores Práticas

- Gerenciamento de dependências com cache
- Workflows separados para diferentes estágios
- Varreduras de segurança antes da implantação
- Configurações específicas por ambiente

## Comandos do Makefile

O projeto inclui um Makefile com atalhos para tarefas comuns:
- `make install`: Instalar dependências
- `make lint`: Verificar qualidade do código
- `make test`: Executar testes
- `make deploy`: Implantar no ambiente especificado

## Pré-requisitos

- Python 3.12
- Poetry
- Credenciais AWS
- Terraform CLI