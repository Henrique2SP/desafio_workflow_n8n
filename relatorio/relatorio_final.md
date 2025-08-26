# Relatório do Desafio: Orquestração de IA com n8n

*Autor:* Henrique Sávio Silva Pacheco
*Data:* 25 de agosto de 2025

## 1. Introdução

Este relatório detalha a solução desenvolvida para o Desafio Técnico de Orquestração de IA da Facilit Tecnologia S.A. O objetivo foi construir um sistema de Business Intelligence conversacional, onde um usuário pode fazer perguntas em linguagem natural sobre eventos da empresa e receber respostas precisas, geradas por uma inteligência artificial que consulta um banco de dados centralizado.

A ferramenta n8n foi utilizada como o motor central, orquestrando tanto a migração inicial de dados de planilhas no google sheets para o banco de dados quanto o fluxo de perguntas e respostas da IA. 

## 2. Arquitetura da Solução

Para criar um sistema robusto e fácil de gerenciar, a solução foi dividida em três containers principais que operam de forma integrada dentro de um ambiente Docker. O Docker garante que todo o sistema possa ser executado em qualquer máquina de forma consistente. 
A arquitetura é composta por:

* *Banco de Dados (PostgreSQL):* Funciona como o nosso "arquivo central". É um banco de dados PostgreSQL que armazena (com uma automação do n8n) todas as informações sobre os eventos das agendas de IA, Marketing e RH. Ele vive em seu próprio container Docker para garantir isolamento e segurança.

* *API (Back-end em Python/FastAPI):* A API é a "tradutora" do banco de dados e o n8n. Em vez de permitir que o n8n acesse o banco diretamente, ele se comunica com a API. Ela recebe pedidos como "insira este novo evento em IA" ou "me diga a data do evento wiki Facilit" e os traduz em comandos seguros para o banco de dados. Utilizar FastAPI permitiu a criação de uma API rápida e com documentação automática (swagger). A API também roda em seu próprio container. 

* *Orquestrador (n8n):* O n8n é a automação de toda a operação. Ele executa dois fluxos de trabalho (workflows) principais:
    1.  *Workflow de Migração (ETL):* Um workflow que lê os dados das 3 planilhas do Google Sheets e usa a API para salvá-los de forma organizada no banco de dados.
    2.  *Workflow de IA Conversacional (Consulta):* O cérebro do projeto. Ele é responsável pela interação com o usuário, usando a Inteligência Artificial para entendê-las, comanda tools que usam a API para BUSCAR as informações relevantes, ADICIONAR eventos, ALTERAR eventos e, por fim, usa a IA novamente para construir uma resposta amigável.

Todos esses três componentes são gerenciados por um único arquivo, o docker-compose.yml, que permite iniciar ou parar todo o sistema com um único comando. 

## 3. Organização e Segurança:
- Só precisa rodar o docker-compose para ter acesso a toda aplicação.
- .env para manter a segurança de informações sensíveis.
- Interação com o banco de dados apenas no arquivo database.py.
- Fiz um models.py para padronizar o evento (Não obrigatório, mas uma boa prática).

## 4. Como Configurar e Rodar o Projeto

Para que qualquer pessoa possa testar a solução, o processo de configuração foi simplificado ao máximo, visando uma boa "Developer Experience (DX)".

*Pré-requisitos:*
* Git, Docker e Docker Compose instalados na máquina.

*Passo a Passo:*

1.  *Clonar o Repositório:* Primeiro, é necessário baixar o projeto do GitHub para a máquina local: git clone https://github.com/Henrique2SP/desafio_workflow_n8n.git.
2.  *Configurar as Variáveis de Ambiente:* Na raiz do projeto, existe um arquivo de exemplo chamado .env.example. É preciso criar uma cópia dele e renomeá-la para .env. Este arquivo conterá as informações sensíveis, como as senhas do banco de dados e a chave de acesso para a API da OpenAI.
3.  *Iniciar o Ambiente:* Com o terminal aberto na pasta raiz do projeto, basta executar um único comando:
    bash
    docker-compose up --build
    
    * Este comando lê o arquivo docker-compose.yml, constrói a imagem da API com o código mais recente, baixa as imagens do PostgreSQL e n8n, e inicia os três containers de forma integrada.
4.  *Acessar os Serviços:* Após a inicialização, os serviços estarão disponíveis nos seguintes endereços:
    * *API:* http://localhost:8000 (com documentação interativa em /docs).
    * *n8n:* http://localhost:5678.

## 5. Detalhes da Implementação de IA no n8n

A inteligência do sistema reside no segundo workflow (nomeado 'Consulta') do n8n, que utiliza um nó chamado *AI Agent*. Esta abordagem é limpa e poderosa. 

* *Lógica do Fluxo:*
    1.  Um *Webhook* atua como a porta de entrada, aguardando perguntas de usuários no formato {"pergunta": "..."}. 
    2.  A pergunta é enviada ao nó *AI Agent*, que funciona como o cérebro e está conectado com um modelo OpenAI. Foi utilizado o modelo 3.5-turbo.
    3.  O agente recebe a pergunta e a analisa com base em instruções pré-definidas (o prompt).
    4.  Ele percebe que, para responder e para executar a tool corretamente, precisa de dados. 
    5.  O Agente aciona como solicitado alguma tool (buscar_eventos, inserir_eventos, atualizar_eventos) *HTTP Request*, dependendo do pedido do usuário.

        Opções:
        -  Uma tool que faz uma chamada para a API (GET http://api:8000/eventos) para buscar a lista completa de eventos do banco de dados. 
        -  Uma tool que faz uma chamada para a API (POST http://api:8000/eventos) para adicionar um evento ao banco.
        -  Uma tool que faz uma chamada para a API (PUT http://api:8000/eventos/{id}) para alterar um evento que já foi adicionado no banco anteriormente.

    6.  A informação retornada pela API são entregues de volta ao AI Agent.
    7.  Com a pergunta original e os dados do banco em mãos, o agente usa o poder do modelo de linguagem (GPT) para encontrar a informação específica e formular uma resposta final em português.
    8.  Essa resposta é enviada de volta pelo Webhook ao usuário. 

* *Prompt (Instrução do Agente):* A instrução principal dada ao agente é bem explicativa, para mantê-lo focado (o que também funciona como um guardrail) e ensiná-lo sobre como orquestrar as tools:
    
        Você é o Assistente da Facilit, um IA amigável e profissional, especialista na tabela Eventos. Sua comunicação deve ser simples, clara e positiva.

        ## DIRETRIZES:

        - Escopo Fixo: Responda apenas sobre eventos. Para outros assuntos, recuse educadamente.

        - Seja Conciso: Entregue somente o que foi pedido, sem informações técnicas ou detalhes extras.

        - Tom e Formato:

        - Use um tom conversacional e profissional.

        - Formato de data: AAAA-MM-DD.

        - Use emojis sutis para cordialidade (ex: 😊, 📅, ✅).

        - Casos de Resposta:

        - Sucesso: Apresente os resultados de forma limpa e direta.

        - Sem resultados: "Não encontrei eventos com esses critérios, mas posso ajudar a buscar de outra forma se quiser 😊."

        - Erro: "Tive um probleminha ao consultar os eventos. Pode tentar novamente em alguns instantes, por favor?"

        - Ambíguo: Peça esclarecimentos (ex: "Claro! Você quer ver só os nomes ou todos os detalhes dos eventos?").

        - Capacidades Técnicas:

        - Métodos permitidos: GET, POST, PUT.

        - Campos do banco: evento (string), data (string), descricao (string), engajamento (int), status (string), origem (string).

        - Alias: marketing se refere a MKT.

        ## MANUAL DE USO DA TOOL

        Para usar o PUT, primeiro você SEMPRE *NÃO PULE ESTA ETAPA, ELA É CRUCIAL PARA A BOA FUNCIONALIDADE DA TOOL* tem que fazer uma requisição no GET, e ver qual o ID da entidade que o usuário está procurando para mudar (veja a mais semelhante, pois podem haver erros de digitação).
        Depois, você deve preencher o campo do endpoint desse jeito:

        http://api:8000/eventos/{{id da entidade que você achou no get}}

        além disso, você deve preencher as informações (variáveis) do PUT de acordo com o que o usuário pediu.
        
    

* *Ferramenta (Tool):* Foram definidas duas ferramentas para o agente:
    TOOL 1
    * *Nome:* buscar_eventos
    * *Descrição para a IA:* "Use esta ferramenta para buscar e obter uma lista de todos os eventos agendados da empresa. A ferramenta não precisa de parâmetros, ela retorna os eventos de acordo com o pedido feito."
    * *Ação:* A ferramenta está configurada para fazer "HTTP Request" que busca os dados na API.

    TOOL 2
    * *Nome:* inserir_evento
    * *Descrição para a IA:* "Faz um request HTTP de acordo com a pergunta do usuário, passe a consulta no formato json especificado no body."
    * *Ação:* A ferramenta está configurada para fazer um "HTTP Request" que insere os dados na API.

    TOOL 3
     * *Nome:* atualizar_evento
    * *Descrição para a IA:* "Faz um request HTTP de acordo com a solicitação do usuário, que vai passar as informações para serem alteradas num evento já existente que o usuário vai dizer"
    * *Ação:* A ferramenta está configurada para fazer "HTTP Request" que atualiza dados na API.

## 6. Dificuldades Enfrentadas

Durante o desenvolvimento, alguns desafios interessantes surgiram, levando a importantes decisões de arquitetura e implementação:

* *Inconsistência dos Dados de Origem:* A maior dificuldade foi lidar com as diferenças estruturais entre as três planilhas. Inicialmente, a análise indicou que as colunas eram diferentes, o que levou a uma refatoração complexa para um modelo de três tabelas no banco de dados. Após uma análise mais detalhada das colunas, percebeu-se que a melhor abordagem seria reverter para uma *tabela única, porém mais flexível*. O design final do banco de dados agora possui colunas genéricas (como metrica_nome e metrica_valor) que conseguem acomodar as variações de "Engajamento" e "ALCANCE", tornando a solução mais simples e robusta.

* *Erros de Formato JSON no n8n:* Durante a migração de dados, ocorreram erros persistentes de "JSON inválido". A depuração revelou que os dados vindos das planilhas continham caracteres especiais (principalmente aspas duplas " em nomes de eventos). A solução foi implementar um pré-tratamento de dados no n8n, utilizando a função JSON.stringify() para "escapar" esses caracteres, garantindo que o JSON enviado para a API fosse sempre sintaticamente correto.

* *Sincronização do Ambiente Docker:* Em alguns momentos, o sistema apresentava erros de "coluna não encontrada" mesmo após a correção do código. A causa era o cache do Docker. O banco de dados persistia em um volume com a estrutura de tabela antiga. Foi necessário aprender a forçar uma limpeza completa do ambiente com o comando docker-compose down -v para garantir que o banco e a API fossem recriados do zero com as definições mais recentes, resolvendo o problema de "estado fantasma".

* *Dificuldades na engenharia de prompt:* Em alguns momentos, foi desafiador fazer com que o modelo agisse completamente de acordo com o descrito no prompt. Tive alguns problemas com alucinações e respostas inesperadas, mesmo quando dava uma instrução clara. Foi difícil chegar numa resposta que o robô seguisse por completo.


## 7. Uso da IA:
Utilizei o modelo Gemini 2.5pro para:
- Sintaxe do back em fastapi
- Criar arquivo docker-compose

Utilizei o modelo GPT 4o-mini para:
- Adaptar o prompt para melhor desempenho do agente
- Ajudar na formatação do markdown