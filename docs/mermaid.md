```mermaid
graph TD
    np[networking policy = cilium] -->|requires| edp[ebpf_data_plane = cilium]
    edp -->|requires| d[pod subnet OR overlay network mode]
    edp -->|requires| npa[network_plugin = azure]
```


# Documentação CI/CD com Mermaid e Sphinx

## Introdução
Este documento descreve o processo completo de CI/CD implementado usando GitHub Actions, Terraform, Python, segurança e análise de custos.

## Visão Geral (Mermaid)

```mermaid
graph TD

%% Eventos do GitHub
event_push_main_staging([Push em main/staging]) -->|Dispara| Continuous_Deployment
event_pr([Pull Request]) -->|Dispara| Continuous_Integration

%% Continuous Deployment Workflow
subgraph Continuous_Deployment
    direction TB
    Determine_Environment --> Testes
    Testes --> Security_Scan
    Security_Scan --> Check_PR
    Check_PR --> Terraform_Deploy
end

%% Continuous Integration Workflow
subgraph Continuous_Integration
    direction TB
    Testes_CI --> Security_Scan_CI
    Security_Scan_CI --> Check_PR_CI
    Security_Scan_CI --> Infracost_Analysis
    Check_PR_CI --> Terraform_Dev
    Terraform_Dev --> PR_Comment
    Infracost_Analysis --> PR_Comment
end

%% Workflows Reutilizáveis
Security_Scan -.->|Usa| Trivy
Terraform_Deploy -.->|Usa| Terraform_Core
Terraform_Dev -.->|Usa| Terraform_Core
Infracost_Analysis -.->|Usa| Infracost_Workflow
PR_Comment -.->|Usa| PR_Comment_Workflow

%% Actions externas
Testes -->|Executa| Lint_and_Tests
Testes_CI -->|Executa| Lint_and_Tests

```

## Explicação dos Workflows

### Continuous Deployment

Este workflow é acionado por push nas branches `main` ou `staging` ou manualmente (`workflow_dispatch`). As etapas incluem:
- Determinação do ambiente de implantação (stg ou prod)
- Testes unitários e lint do código Python
- Scan de segurança com Trivy
- Checagem de PR aberta
- Deploy com Terraform no ambiente determinado

### Continuous Integration

Este workflow é acionado em pushes em outras branches e abertura de Pull Requests. As etapas incluem:
- Testes unitários e lint do código Python
- Scan de segurança com Trivy
- Checagem de PR aberta
- Análise de custos de infraestrutura com Infracost
- Deploy com Terraform no ambiente dev
- Comentário automático na PR com resultados do CI

## Workflows Compartilhados e Ferramentas

- **Security Scan**: Usa Trivy para scan de vulnerabilidades no sistema de arquivos.
- **Terraform Core**: Realiza validação, planejamento, e aplicação/destroy de recursos Terraform.
- **Infracost Analysis**: Avalia custos associados aos recursos Terraform.
- **PR Comment Workflow**: Posta comentários automatizados nas PRs com detalhes do processo de CI/CD.

## Dependências
Dependabot é utilizado para atualização semanal de:
- Dependências Python (pip)
- Ações do GitHub
- Imagens Docker