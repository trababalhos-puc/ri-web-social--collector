# Project Template

## Descrição
Este é um projeto de desenvolvimento com infraestrutura automatizada em nuvem, utilizando Terraform para provisionamento e GitHub Actions para CI/CD. O projeto está estruturado seguindo boas práticas de DevOps e desenvolvimento Python.

## Requisitos

- Python 3.8+
- Docker e Docker Compose
- AWS CLI configurado
- Terraform
- Poetry (gerenciador de dependências Python)
- Make

## Configuração do Ambiente

### Variáveis de Ambiente

Copie o arquivo `.env.example` para criar seu arquivo `.env`:

```bash
cp .env.example .env
```

Em seguida, preencha as variáveis de ambiente necessárias.

### Instalação de Dependências

Usando Poetry:
```bash
poetry install
```

Ou usando pip:
```bash
pip install -r requirements.txt
# Para ambiente de desenvolvimento
pip install -r requirements-dev.txt
```

### Configuração Inicial

Execute o script de inicialização para configurar os recursos iniciais na AWS na maquina LOCAL:
```bash
cd init
./deploy.sh
```

## Execução Local

### Usando Docker

```bash
docker-compose up
```

### Sem Docker

```bash
make run
```

## Implementação na Nuvem

### Infraestrutura

O projeto utiliza Terraform para gerenciar a infraestrutura na AWS. Os ambientes disponíveis são:

- Desenvolvimento (dev)
- Staging (stg)
- Produção (prod)

Para implantar a infraestrutura:

```bash
cd infra
./deploy.sh [dev|stg|prod]
```

### CI/CD

A integração e entrega contínuas são gerenciadas por GitHub Actions. Os fluxos de trabalho incluem:

- CI: Verificação de código, testes e análise estática
- CD: Implantação automática para os ambientes
- Análise de segurança
- Revisão de dependências
- Estimativa de custos com Infracost

## Estrutura do Projeto

```
.
├── .github/               # Fluxos de trabalho e templates do GitHub
├── docs/                  # Documentação
├── infra/                 # Definições de infraestrutura com Terraform
│   ├── envs/              # Configurações específicas de ambiente
│   └── modules/           # Módulos Terraform reutilizáveis
├── init/                  # Scripts de inicialização da infraestrutura
├── monitoring/            # Ferramentas de monitoramento
├── src/                   # Código-fonte da aplicação
│   └── project/           # Pacote principal do projeto
└── tests/                 # Testes automatizados
```

## Documentação

A documentação completa do projeto pode ser gerada usando Sphinx:

```bash
cd docs
make html
```

Documentação de arquitetura disponível em `docs/architecture.md`.

## Contribuição

Por favor, leia o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre o processo de envio de pull requests.

### Pre-commit Hooks

Este projeto utiliza pre-commit hooks para garantir a qualidade do código:

```bash
pre-commit install
```

## Monitoramento

O projeto inclui métricas Prometheus para monitoramento em `monitoring/prometheus_metrics.py`.

## Testes

Execute os testes com o comando:

```bash
make test
```

## Segurança

Consulte [SECURITY.md](SECURITY.md) para informações sobre políticas de segurança e como relatar vulnerabilidades.

## Licença

Este projeto está licenciado sob os termos da licença definida no arquivo [LICENSE](LICENSE).

## Changelog

Veja o arquivo [CHANGELOG.md](CHANGELOG.md) para um histórico de todas as alterações do projeto.