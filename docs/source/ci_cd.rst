=================================
Integração Contínua e Implantação
=================================

### Fluxo de Trabalho do GitHub Actions

Os fluxos são acionados automaticamente por push nas branches `main`, `staging` ou manualmente.

#### Diagrama do fluxo CI/CD:

.. mermaid:: mermaid.mmd
    :zoom:


Determinação dinâmica do ambiente:

- Branch `main` → Produção
- Branch `staging` → Staging
- Manual → Definido pelo usuário

### Jobs Específicos

- **Testes**: Python (Pytest), Lint (Ruff)
- **Segurança**: Scan de segurança (Trivy)
- **Terraform**: Provisionamento automático AWS