# Desafio de Orquestração de IA com n8n

Este repositório contém a solução completa para o Desafio Técnico de Orquestração de IA, que consiste em um sistema de *Business Intelligence* conversacional. A solução permite que um usuário faça perguntas em linguagem natural e receba respostas precisas, consultadas de um banco de dados populado com informações de planilhas do Google Sheets.

## 🏛️ Arquitetura da Solução

O projeto é totalmente containerizado com Docker e orquestrado via Docker Compose, garantindo um ambiente de desenvolvimento e execução simples e consistente. A arquitetura é composta por três serviços principais:

1.  **API (FastAPI + Python):** Um back-end robusto que serve como a camada de acesso ao banco de dados. Ele expõe endpoints para operações CRUD (Criar, Ler, Atualizar, Deletar) sobre os dados dos eventos.
2.  **Banco de Dados (PostgreSQL):** Armazena todas as informações dos eventos, que são migradas das planilhas.
3.  **Orquestrador (n8n):** O cérebro do projeto, responsável por dois workflows:
    * **Migração de Dados (ETL):** Um fluxo que lê os dados das planilhas do Google, os pré-processa e os insere no banco de dados através da API.
    * **Agente de IA Conversacional:** Um fluxo que recebe perguntas de usuários via Webhook, utiliza um modelo de linguagem da OpenAI para interpretar a pergunta, decide qual ferramenta usar, consulta a API para obter os dados e formula uma resposta em linguagem natural.

```
Usuário --> Webhook (n8n) --> AI Agent (n8n) --(chama ferramenta)--> API (FastAPI) --> Banco de Dados (PostgreSQL)
   ^                                                                                         |
   |                               (resposta final)                                          |
   +-----------------------------------------------------------------------------------------+
```

## 🛠️ Tecnologias Utilizadas

- **Back-end:** Python, FastAPI
- **Banco de Dados:** PostgreSQL
- **Orquestração:** n8n (Self-Hosted)
- **Containerização:** Docker, Docker Compose
- **IA:** OpenAI (GPT)
- **Bibliotecas Python:** `psycopg2-binary`, `pydantic`

## 🚀 Como Configurar e Rodar o Projeto

Siga os passos abaixo para ter todo o ambiente rodando localmente.

### Pré-requisitos

-   [Git](https://git-scm.com/downloads)
-   [Docker](https://www.docker.com/products/docker-desktop/) e Docker Compose

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/nome-do-repositorio.git](https://github.com/seu-usuario/nome-do-repositorio.git)
    cd nome-do-repositorio
    ```

2.  **Configure as variáveis de ambiente:**
    Crie uma cópia do arquivo de exemplo `.envexample` e renomeie-a para `.env`.
    ```bash
    cp .envexample .env
    ```
    Abra o arquivo `.env` e preencha com suas credenciais:
    ```env
    # Credenciais para o banco de dados PostgreSQL
    POSTGRES_USER=seu_usuario
    POSTGRES_PASSWORD=sua_senha_super_secreta
    POSTGRES_DB=agendas_db

    # Sua chave da API da OpenAI (necessária para a Etapa 3)
    OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

3.  **Inicie os containers:**
    Execute o seguinte comando na raiz do projeto. Ele irá construir a imagem da API, baixar as imagens do PostgreSQL e n8n, e iniciar todos os serviços.
    ```bash
    docker-compose up --build
    ```
    Aguarde alguns minutos até que os logs se estabilizem. Os serviços estarão disponíveis nos seguintes endereços:
    -   **API (Docs):** `http://localhost:8000/docs`
    -   **n8n:** `http://localhost:5678`

## 🤖 Como Usar a Automação

### 1. Migração de Dados (ETL)

Após iniciar o ambiente, a primeira coisa a fazer é popular o banco de dados.

1.  Acesse a interface do n8n em `http://localhost:5678`.
2.  Crie sua conta de administrador.
3.  Importe o workflow de migração (localizado em `/workflows/ETL.json`).
4.  Configure as credenciais do Google Sheets no nó correspondente (acesse `https://console.cloud.google.com/auth` para criar uma credencial).
5.  Execute o workflow manualmente clicando em "Execute Workflow". Os dados das planilhas serão enviados para o banco de dados.

### 2. Consulta com a Inteligência Artificial

Com o banco de dados populado, você pode interagir com o agente de IA.

1.  Importe o workflow de IA (`/workflows/consulta.json`) no n8n.
2.  Configure as credenciais da OpenAI no nó "OpenAI Chat Model".
3.  Ative o workflow.
4.  Copie a URL de produção do nó Webhook.
5.  Abra um terminal e use o `curl` para fazer uma pergunta. Substitua a URL e a pergunta conforme necessário.

**Exemplo de consulta:**
```bash
curl -X POST \
-H "Content-Type: application/json" \
-d '{"prompt": "Quais eventos de marketing estão planejados para setembro?"}' \
{url}
```

**Exemplo de adição:**
```bash
curl -X POST \
-H "Content-Type: application/json" \
-d '{"pergunta": "Por favor, crie um evento chamado Workshop de Inovação para o dia 10 de outubro, responsável Ana, depto de IA"}' \
{url}
```

A resposta do `curl` será um JSON contendo a resposta formulada pela IA.
```json
{
  "output": "O evento de marketing planejado para setembro é o 'Facilit Comunica', que ocorrerá de 10/09/2025 a 11/09/2025."
}
```

## 📁 Estrutura do Projeto

```
.
├── api/                # Contém os códigos do back da API em FastAPI
├── workflows/          # Contém os arquivos JSON dos workflows do n8n
├── relatorio/          # Contém o relatório final em .md
├── .env.example        # Arquivo de exemplo para as variáveis de ambiente
├── docker-compose.yml  # Arquivo de orquestração dos containers
└── README.md           # Este arquivo
```
