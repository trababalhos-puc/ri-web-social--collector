# Projeto de Extração e Análise de Dados IPEA

## 1. O que é este repositório

Este repositório contém uma solução completa para extração, processamento e armazenamento de dados econômicos do portal IPEADATA. O sistema automatiza a coleta de indicadores e documentos através de web scraping, converte PDFs em formato HTML para facilitar a análise e armazena os resultados de forma estruturada. A solução é implementada como um serviço programado que pode ser executado localmente para testes ou implantado na AWS para operação contínua.

O projeto inclui:
- Um extrator baseado em Selenium para navegar e coletar dados do site IPEADATA
- Um conversor de PDF para HTML para processamento de documentos
- Infraestrutura como código (IaC) usando Terraform para provisionamento na AWS
- Pipeline de CI/CD com GitHub Actions para desenvolvimento contínuo

## 2. Dependências mínimas

### Para execução local
- Docker e Docker Compose

### Para implantação na AWS
- Conta AWS com direitos de administrador
- AWS CLI configurado
- Terraform 1.8.3+
- Docker instalado (para build local de imagens)

## 3. Organização de arquivos

```
/
├── .github/                # Configurações e workflows do GitHub Actions
│   ├── workflows/          # Workflows de CI/CD
│   └── deploy/             # Scripts de implantação
│
├── infra/                  # Código Terraform para infraestrutura AWS
│   ├── modules/            # Módulos Terraform
│   │   ├── ecr/            # Elastic Container Registry
│   │   ├── ecs/            # Elastic Container Service
│   │   ├── s3/             # Buckets S3
│   │   └── vpc/            # Configuração de rede
│   └── envs/               # Variáveis por ambiente (dev, stg, prod)
│
├── init/                   # Infraestrutura inicial para CI/CD e backend
│
├── src/                    # Código-fonte da aplicação Python
│   ├── config/             # Configurações da aplicação
│   ├── service/            # Componentes de serviço
│   │   ├── extract.py      # Lógica de extração de dados
│   │   └── convert.py      # Conversão de PDF para HTML
│   ├── entrypoint.sh       # Script de entrada para execução em container
│   ├── main.py             # Ponto de entrada da aplicação
│   ├── Dockerfile          # Definição da imagem Docker
│   └── requirements.txt    # Dependências Python
│
├── Makefile                # Comandos para facilitar operações
└── pyproject.toml          # Configuração do Poetry e dependências
```

## 4. Como executar localmente


### Execução com Docker (recomendado)

1. Navegue até a pasta src:
```bash
cd src
```

2. Execute sem integração com AWS:
```bash
docker-compose up # para iniciar o processo
# docker-compose up -d (caso nao queira acompanhar o processo)
docker-compose down # para finalizar o processo
```

3. Ou para executar com integração com AWS:
```bash
# Configure suas credenciais AWS
aws configure

# Execute usando o Docker Compose com configuração AWS
docker-compose -f docker-compose-aws.yml up
```


Após a execução, os dados extraídos estarão disponíveis:
- Localmente no diretório 'ipea' (se executado sem S3)
- No bucket S3 configurado (se executado com integração AWS)
