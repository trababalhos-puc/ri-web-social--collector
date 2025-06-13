# Projeto de Extração e Análise de Dados IPEA

## 1. O que é este repositório

Este repositório contém uma solução completa para extração, processamento e armazenamento de dados econômicos do portal IPEADATA. O sistema automatiza a coleta de indicadores e documentos através de web scraping, converte PDFs em formato HTML para facilitar a análise e armazena os resultados de forma estruturada. A solução é implementada como um serviço programado que pode ser executado localmente para testes ou implantado na AWS para operação contínua.

O projeto inclui:
- Um extrator baseado em Selenium para navegar e coletar dados do site IPEADATA
- Um conversor de PDF para HTML para processamento de documentos
- Infraestrutura como código (IaC) usando Terraform para provisionamento na AWS
- Pipeline de CI/CD com GitHub Actions para desenvolvimento contínuo
- Sistema de representação e indexação de dados para busca e recuperação de informações

## 2. Dependências mínimas

### Para execução local
- Docker e Docker Compose
- Python 3.10+
- Bibliotecas Python: selenium, requests, beautifulsoup4, boto3, nltk, etc. (ver requirements.txt)

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
│   │   │   ├── s3/         # Buckets S3
│   │   └── vpc/            # Configuração de rede
│   └── envs/               # Variáveis por ambiente (dev, stg, prod)
│
├── init/                   # Infraestrutura inicial para CI/CD e backend
│
├── src/                    # Código-fonte da aplicação Python
│   ├── config/             # Configurações da aplicação
│   ├── service/            # Componentes de serviço
│   │   ├── extract.py      # Lógica de extração de dados
│   │   ├── convert.py      # Conversão de PDF para HTML
│   │   ├── transform.py    # Transformação e mapeamento de documentos
│   │   └── index.py        # Indexação e busca de documentos
│   ├── entrypoint.sh       # Script de entrada para execução em container
│   ├── main.py             # Ponto de entrada da aplicação
│   ├── Dockerfile          # Definição da imagem Docker
│   ├── Dockerfile-index    # Definição da imagem Docker para indexação
│   ├── docker-compose.yml  # Configuração para extração de dados
│   ├── docker-compose-aws.yml # Configuração para extração com AWS
│   ├── docker-compose-index.yml # Configuração para indexação
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
docker compose up # para iniciar o processo
# docker compose up -d (caso nao queira acompanhar o processo)
docker compose down # para finalizar o processo
```

3. Ou para executar com integração com AWS:
```bash
# Configure suas credenciais AWS
aws configure

# Execute usando o Docker Compose com configuração AWS
docker compose -f docker-compose-aws.yml up
```

Após a execução, os dados extraídos estarão disponíveis:
- Localmente no diretório 'ipea' (se executado sem S3)
- No bucket S3 configurado (se executado com integração AWS)

## 5. Sistema de Representação/Indexação

O projeto implementa um sistema avançado de representação e indexação de documentos que permite busca eficiente nos dados extraídos do IPEA. A abordagem utiliza processamento de linguagem natural e índices invertidos para otimizar a recuperação de informações.

![index](./src/index_comparison.png)

### 5.1 Características do Sistema de Indexação

- **Processamento Textual**: Normalização, tokenização, remoção de stopwords e stemming para português.
- **Índice Invertido**: Estrutura de dados otimizada para buscas por termo.
- **Múltiplas Configurações**: Suporte para diferentes modos de indexação (básico, sem stopwords, com stemming, bigramas, shingles).
- **Ranking TF-IDF**: Modelo de relevância baseado em Term Frequency-Inverse Document Frequency.
- **Análise Comparativa**: Métricas para avaliar desempenho das diferentes configurações (tempo, espaço, qualidade).

### 5.2 Como usar o sistema de indexação

#### 5.2.1 Execução via Docker (recomendado)

Para executar o sistema de indexação usando Docker, temos duas opções:

**Opção 1: Usando Docker Compose:**

```bash
# Construir e iniciar o container
docker compose -f docker-compose-index.yml up --build

# Ou executar em segundo plano (modo detached)
docker compose -f docker-compose-index.yml up --build -d
```

**Opção 2: Para entrar no container e executar scripts interativamente:**

```bash
# Iniciar o container em modo detached
docker compose -f docker-compose-index.yml up --build -d

# Verificar o nome do container em execução
docker ps

# Acessar o container (substitua "nome_do_container" pelo nome real)
docker exec -it nome_do_container /bin/bash

# Dentro do container, executar o script de indexação
python index.py

# Para sair do container
exit
```

**Opção 3: Iniciar diretamente com shell interativo:**

```bash
# Iniciar o container com um shell interativo
docker compose -f docker-compose-index.yml run --rm ipea-indexacao /bin/bash

# Dentro do container, executar o script
python index.py
```

**Opção 4: Usando Docker diretamente:**

```bash
# Construir a imagem
docker build -t ipea-indexacao -f Dockerfile-index .

# Executar o container
docker run --rm -v $(pwd):/app ipea-indexacao python index.py
```

### 5.3 Interface Web Interativa (Streamlit)

O sistema agora inclui uma **interface web completa** desenvolvida com Streamlit, proporcionando uma experiência de usuário intuitiva e profissional para interação com o sistema de recuperação de informação.

#### 5.3.1 Execução da Interface

```bash
poetry shell
poetry install
cd src
streamlit run app.py

# A interface estará disponível em: http://localhost:8501
```

#### 5.3.2 Funcionalidades da Interface

**Dashboard Principal:**
- **Configuração Dinâmica**: Inicialização automática do sistema via interface
- **Seleção de Índices**: Escolha entre 5 tipos diferentes de indexação
- **Busca Inteligente**: Campo de busca com processamento em tempo real
- **Resultados Ranqueados**: Listagem ordenada por relevância (TF-IDF)
- **Abertura de Documentos**: Botões para abrir arquivos HTML diretamente no navegador

**Tipos de Índice Disponíveis:**

| Tipo | Descrição | Uso Recomendado |
|------|-----------|-----------------|
| **Básico** | Processamento padrão com stopwords e stemming | Buscas gerais |
| **Sem Stopwords** | Mantém palavras originais, remove stopwords | Termos específicos |
| **Com Stemming** | Reduz palavras ao radical (casa, casas → cas) | Variações de palavras |
| **Bigramas** | Indexa pares de palavras consecutivas | Nomes próprios, frases |
| **Shingles** | Combina 1, 2 e 3 palavras (n-gramas) | Busca flexível com contexto |

**Recursos Avançados:**
- **Comparação de Índices**: Análise lado a lado de diferentes estratégias
- **Estatísticas Detalhadas**: Métricas de vocabulário, tempo e memória
- **Explorador de Documentos**: Navegação e filtros por data/nome
- **Análise de Performance**: Tempo de busca e uso de recursos

#### 5.3.3 Arquitetura da Interface

```python
class IPEANavigator:
    def __init__(self):
        self.analyzer = None          # Sistema de análise de índices
        self.documents = {}           # Documentos carregados
        self.json_data = {}          # Dados do mapeamento
    
    def initialize_index(self):      # Inicialização do sistema
    def load_data(self):            # Carregamento de dados
    def get_full_path(self):        # Resolução de caminhos
    def open_html_file(self):       # Abertura de documentos
```

### 5.4 Sistema de Recuperação e Ranking

#### 5.4.1 Algoritmo TF-IDF Implementado

O sistema utiliza **Term Frequency-Inverse Document Frequency** para ranking de relevância:

```python
TF(t,d) = (Frequência do termo t no documento d) / (Total de termos no documento d)
IDF(t,D) = log(Total de documentos / Documentos que contêm o termo t)
TF-IDF(t,d,D) = TF(t,d) × IDF(t,D)
```

**Vantagens da Implementação:**
- **Normalização**: Documentos longos não dominam os resultados
- **Raridade**: Termos raros recebem maior peso
- **Relevância**: Balanceamento entre frequência local e global

#### 5.4.2 Otimizações de Performance

- **Índices Invertidos**: Busca O(1) por termo
- **Processamento Paralelo**: Múltiplos workers para criação de índices
- **Cache Inteligente**: Reutilização de índices já construídos
- **Compressão de Memória**: Estruturas otimizadas para grandes volumes

### 5.5 Análise Comparativa de Índices

O sistema gera automaticamente **análises comparativas** entre diferentes estratégias de indexação:

#### 5.5.1 Métricas Coletadas

| Métrica | Descrição | Importância |
|---------|-----------|-------------|
| **Vocabulário** | Número único de termos | Cobertura linguística |
| **Termos/Documento** | Média de termos por documento | Granularidade |
| **Tempo de Construção** | Duração da indexação | Escalabilidade |
| **Uso de Memória** | RAM utilizada pelos índices | Eficiência |
| **Tempo de Busca** | Latência das consultas | Experiência do usuário |

#### 5.5.2 Resultados Típicos

```bash
Índice 'básico': 12.5MB, 15,432 termos, 2.3s construção
Índice 'bigramas': 45.2MB, 89,654 termos, 8.7s construção
Índice 'shingles': 78.1MB, 156,789 termos, 15.2s construção
```

### 5.6 Funcionalidades Avançadas

#### 5.6.1 Explorador de Documentos

- **Filtros por Data**: Navegação cronológica dos documentos
- **Busca por Nome**: Filtros textuais para localização rápida
- **Preview do Conteúdo**: Visualização prévia antes da abertura
- **Estatísticas de Coleção**: Informações sobre o corpus

#### 5.6.2 Integração com Sistema Operacional

```python
def open_html_file(self, file_path):
    if platform.system() == "Windows":
        os.startfile(abs_path)
    elif platform.system() == "Darwin":
        subprocess.run(["open", abs_path])
    else:
        subprocess.run(["xdg-open", abs_path])
```

### 5.7 Tratamento de Erros e Robustez

- **Validação de Caminhos**: Verificação de existência de arquivos
- **Fallback Automático**: Alternativas quando arquivos não existem
- **Logging Detalhado**: Rastreamento de erros e debugging
- **Recuperação Graceful**: Sistema continua funcionando mesmo com falhas parciais

## 6. Manual do Usuário

### 6.1 Primeira Execução

1. **Iniciar a Aplicação**
   ```bash
   streamlit run app.py
   ```

2. **Configurar o Sistema**
    - Acesse a sidebar esquerda
    - Clique em "Inicializar Sistema"
    - Aguarde o carregamento (pode demorar alguns minutos)

3. **Verificar Status**
    - Confirme que aparece "Sistema Ativo" na sidebar
    - Verifique as métricas de documentos e índices

### 6.2 Realizando Buscas

1. **Escolher Estratégia**
    - Selecione o tipo de índice adequado
    - Leia a descrição e uso recomendado

2. **Digite a Consulta**
    - Use termos específicos para melhores resultados
    - Exemplo: "David Richardson", "política monetária"

3. **Analisar Resultados**
    - Documentos ordenados por relevância
    - Scores TF-IDF visíveis
    - Botões para abertura direta

### 6.3 Funcionalidades Especiais

- **Comparação**: Marque "Comparar com outros índices"
- **Estatísticas**: Ative "Mostrar Estatísticas" para métricas
- **Exploração**: Use "Explorar Documentos" para navegação

## 7. Decisões de Projeto e Justificativas

### 7.1 Escolha do Streamlit

**Motivação**: Interface web rápida e interativa sem complexidade de desenvolvimento web tradicional.

**Vantagens**:
- Desenvolvimento ágil com Python puro
- Componentes ricos para visualização de dados
- Integração natural com pandas e matplotlib
- Deploy simples e direto

### 7.2 Múltiplas Estratégias de Indexação

**Motivação**: Diferentes tipos de consulta requerem diferentes abordagens de indexação.

**Implementação**:
- **Básico**: Para usuários iniciantes
- **Sem Stopwords**: Para termos técnicos específicos
- **Stemming**: Para variações morfológicas
- **Bigramas**: Para nomes próprios e entidades
- **Shingles**: Para busca contextual avançada

### 7.3 Arquitetura Modular

**Componentes Separados**:
```
├── service/
│   ├── extract.py      # Extração de dados
│   ├── convert.py      # Conversão PDF→HTML
│   ├── transform.py    # Mapeamento de documentos
│   └── index.py        # Sistema de indexação
└── app.py              # Interface do usuário
```

**Benefícios**:
- Facilita manutenção e testes
- Permite evolução independente de componentes
- Reutilização de código entre diferentes interfaces

## 8. Melhorias Implementadas na Etapa Final

### 8.1 Interface de Usuário Completa

- **Dashboard Profissional**: Layout moderno com sidebar e métricas
- **Feedback Visual**: Spinners, progress bars e mensagens de status
- **Responsividade**: Adaptação automática a diferentes tamanhos de tela

### 8.2 Sistema de Abertura de Documentos

- **Integração OS**: Abertura automática no navegador padrão
- **Validação de Caminhos**: Verificação prévia de existência
- **Feedback Imediato**: Confirmação visual das ações

### 8.3 Análise Comparativa Avançada

- **Métricas Múltiplas**: Tempo, memória, vocabulário, precisão
- **Visualização Tabular**: Comparação lado a lado dos índices
- **Recomendações**: Sugestões de uso para cada tipo de índice

### 8.4 Explorador de Documentos

- **Filtros Dinâmicos**: Por data, nome e conteúdo
- **Preview Inteligente**: Visualização prévia do conteúdo
- **Navegação Paginada**: Listagem eficiente de grandes coleções

## 9. Próximos Passos e Evolução

### 9.1 Melhorias Planejadas

- **Cache de Consultas**: Armazenamento de buscas frequentes
- **Exportação de Resultados**: Download em CSV/JSON
- **Busca Semântica**: Integração com embeddings de palavras
- **Interface Mobile**: Otimização para dispositivos móveis

### 9.2 Escalabilidade

- **Índices Distribuídos**: Suporte para múltiplos servidores
- **Atualização Incremental**: Adição de novos documentos sem reconstrução
- **API REST**: Acesso programático ao sistema de busca

### 9.3 Análise Avançada

- **Clustering de Documentos**: Agrupamento automático por temas
- **Visualização de Tópicos**: Mapas semânticos da coleção
- **Trending**: Identificação de temas emergentes

## 10. Conclusão

O sistema desenvolvido representa uma **solução completa e profissional** para recuperação de informação em documentos do IPEA. A combinação de múltiplas estratégias de indexação, interface intuitiva e análises comparativas oferece uma ferramenta poderosa tanto para usuários finais quanto para pesquisadores interessados em técnicas de RI.

A implementação modular e bem documentada facilita a manutenção e evolução contínua do sistema, estabelecendo uma base sólida para futuras melhorias e adaptações a outros domínios de conhecimento.

## Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue para discutir mudanças significativas antes de submeter um pull request.

## Licença

Este projeto está licenciado sob os termos da licença MIT.