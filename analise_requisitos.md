
# Análise de Requisitos - Sistema BarberFlow

## 1. Introdução

Este documento detalha os requisitos funcionais e não funcionais para o sistema de autoatendimento de barbearias, **BarberFlow**. O objetivo é fornecer uma visão clara e abrangente do sistema a ser desenvolvido, servindo como um guia para as equipes de design, desenvolvimento e teste. O sistema visa modernizar a gestão de barbearias, oferecendo uma solução completa para agendamento online, administração de múltiplos barbeiros, controle financeiro e de estoque, além de uma poderosa integração para automação de atendimento via WhatsApp.

## 2. Visão Geral do Sistema

O BarberFlow será uma plataforma web completa, acessível por diferentes tipos de usuários: clientes, barbeiros e gerentes (administradores). Cada tipo de usuário terá um painel com funcionalidades específicas para suas necessidades, garantindo uma experiência de usuário otimizada e segura. A arquitetura do sistema será baseada em serviços, com uma API RESTful robusta no backend e uma interface de usuário reativa e responsiva no frontend.

## 3. Requisitos Funcionais

### 3.1. Módulos do Sistema

O sistema será composto pelos seguintes módulos principais:

- **Agendamento Online:** Permitirá que os clientes agendem serviços com seus barbeiros preferidos, em horários disponíveis, de forma totalmente online e intuitiva.
- **Gestão de Barbeiros e Serviços:** Os administradores poderão cadastrar, editar e remover barbeiros, bem como os serviços oferecidos pela barbearia, incluindo preços, durações e barbeiros associados.
- **Painel do Cliente:** Uma área dedicada para os clientes gerenciarem seus agendamentos, visualizarem seu histórico e atualizarem suas informações de perfil.
- **Painel do Barbeiro:** Um painel para os barbeiros consultarem suas agendas, confirmarem atendimentos e acompanharem seus repasses financeiros.
- **Painel do Administrador:** O painel central de controle do sistema, onde os gerentes terão acesso a todas as funcionalidades de gestão, incluindo usuários, serviços, finanças, estoque e relatórios.
- **Controle Financeiro:** Um módulo completo para registrar todas as transações financeiras, como pagamentos de serviços, vendas de produtos, compras de insumos e repasses para os barbeiros.
- **Controle de Estoque:** Funcionalidade para gerenciar o estoque de produtos, tanto para venda aos clientes quanto para uso interno dos barbeiros, com alertas de estoque baixo.
- **API RESTful Pública:** Uma API segura e bem documentada que permitirá a integração com outros sistemas, como a automação via n8n para o WhatsApp.
- **Painel de Relatórios e Estatísticas:** Geração de relatórios detalhados e visualização de métricas de desempenho da barbearia.
- **Integração com WhatsApp via n8n:** Automação de interações com clientes via WhatsApp, como agendamento e confirmação de serviços.




### 3.2. Modelos de Dados (Banco de Dados Relacional)

O sistema utilizará um banco de dados relacional para armazenar as informações. Os principais modelos de dados e seus atributos são:

#### Usuários
- `id` (PK)
- `nome` (VARCHAR)
- `e-mail` (VARCHAR, UNIQUE)
- `senha` (VARCHAR, criptografada com bcrypt)
- `tipo` (ENUM: 'cliente', 'barbeiro', 'gerente')
- `foto` (VARCHAR, URL para imagem)
- `telefone` (VARCHAR)

#### Serviços
- `id` (PK)
- `nome` (VARCHAR)
- `descrição` (TEXT)
- `preço` (DECIMAL)
- `duração` (INTEGER, em minutos)
- `barbeiros_disponiveis` (Many-to-Many com Barbeiros)

#### Barbeiros
- `id` (PK)
- `usuario_id` (FK para Usuários)
- `especialidades` (TEXT)
- `horario_de_trabalho` (JSON/TEXT, ex: {'seg': '09:00-18:00'})
- `dias_de_folga` (TEXT, ex: '2025-12-25,2026-01-01')

#### Agendamentos
- `id` (PK)
- `cliente_id` (FK para Usuários)
- `barbeiro_id` (FK para Barbeiros)
- `servico_id` (FK para Serviços)
- `data` (DATE)
- `hora` (TIME)
- `status` (ENUM: 'pendente', 'confirmado', 'realizado', 'cancelado')
- `valor_final` (DECIMAL)
- `forma_pagamento` (VARCHAR)

#### Produtos (Estoque)
- `id` (PK)
- `nome` (VARCHAR)
- `tipo` (ENUM: 'venda', 'uso_interno')
- `quantidade` (INTEGER)
- `unidade` (VARCHAR, ex: 'ml', 'unidade')
- `custo_unitario` (DECIMAL)
- `preço_venda` (DECIMAL, aplicável para tipo 'venda')
- `fornecedor` (VARCHAR)

#### Vendas de Produto
- `id` (PK)
- `produto_id` (FK para Produtos)
- `cliente_id` (FK para Usuários, opcional)
- `quantidade` (INTEGER)
- `valor_total` (DECIMAL)
- `data` (DATETIME)

#### Movimentações Financeiras
- `id` (PK)
- `tipo` (ENUM: 'entrada', 'saída')
- `descrição` (TEXT)
- `valor` (DECIMAL)
- `data` (DATETIME)
- `forma_pagamento` (VARCHAR)
- `associado_a` (VARCHAR, ex: 'venda', 'serviço', 'repasse', 'compra_insumo')

#### Repasses
- `id` (PK)
- `barbeiro_id` (FK para Barbeiros)
- `periodo` (VARCHAR, ex: '2025-07')
- `valor` (DECIMAL)
- `status` (ENUM: 'pago', 'não_pago')
- `observações` (TEXT)




### 3.3. Telas (Interfaces)

As interfaces do sistema serão desenvolvidas para serem responsivas, garantindo uma experiência de usuário consistente em diferentes dispositivos (desktop, tablet, mobile). Serão criados os seguintes painéis:

#### Painel do Cliente
- **Cadastro/Login:** Formulários para criação de conta e acesso ao sistema.
- **Agendamento:** Fluxo intuitivo para escolher serviço, barbeiro, data e hora, e confirmar o agendamento.
- **Histórico de Agendamentos:** Visualização de agendamentos passados e futuros.
- **Gerenciamento de Agendamentos:** Opções para cancelar ou reagendar agendamentos existentes.
- **Notificações:** Exibição de lembretes de agendamento e outras informações relevantes.

#### Painel do Barbeiro
- **Agenda:** Visualização clara dos agendamentos diários, semanais e mensais.
- **Gestão de Atendimentos:** Funcionalidades para confirmar a realização de um atendimento.
- **Histórico de Atendimentos:** Registro de todos os atendimentos realizados pelo barbeiro.
- **Repasses e Comissões:** Acompanhamento detalhado dos valores a receber.

#### Painel do Administrador
- **Dashboard:** Visão geral com KPIs essenciais (atendimentos, receita, barbeiros ativos, produtos em estoque baixo).
- **Gestão de Usuários:** Cadastro, edição e remoção de clientes, barbeiros e outros administradores.
- **Cadastro de Serviços e Produtos:** Interface para gerenciar o catálogo de serviços e o inventário de produtos.
- **Controle de Estoque:** Ferramentas para atualizar quantidades, registrar entradas e saídas de produtos.
- **Fluxo de Caixa:** Relatórios diários e mensais de todas as movimentações financeiras.
- **Cadastro de Repasses:** Geração e gestão dos repasses financeiros para os barbeiros.
- **Relatórios Exportáveis:** Geração de relatórios detalhados que podem ser exportados para análise externa.




### 3.4. API Pública RESTful

Uma API RESTful será desenvolvida para permitir a integração com sistemas externos, como o n8n para automação de WhatsApp. A API será segura, utilizando autenticação via token JWT, e terá os seguintes endpoints:

- `POST /login`: Autenticação de usuários e geração de token JWT.
- `GET /barbeiros`: Lista de todos os barbeiros cadastrados.
- `GET /barbeiros/:id/agenda?data=YYYY-MM-DD`: Agenda de um barbeiro específico para uma determinada data.
- `POST /agendamentos`: Criação de um novo agendamento.
- `GET /agendamentos/:cliente_id`: Histórico de agendamentos de um cliente específico.
- `PATCH /agendamentos/:id`: Atualização do status ou detalhes de um agendamento.
- `GET /servicos`: Lista de todos os serviços oferecidos.
- `GET /produtos`: Lista de todos os produtos disponíveis.
- `POST /vendas-produto`: Registro de uma nova venda de produto.
- `GET /financeiro/fluxo`: Fluxo de caixa financeiro.
- `GET /repasses/:barbeiro_id`: Repasses financeiros de um barbeiro específico.




### 3.5. Automatização via n8n

Para a automação do atendimento via WhatsApp, serão criados webhooks e endpoints específicos que o n8n poderá consumir. Um exemplo de fluxo de automação:

1.  **Usuário envia mensagem no WhatsApp:** O n8n recebe a mensagem e aciona um webhook.
2.  **n8n consulta GET /servicos:** O n8n faz uma requisição à API para obter a lista de serviços disponíveis e exibe as opções ao usuário no WhatsApp.
3.  **Usuário escolhe serviço → n8n chama GET /barbeiros:** Após a escolha do serviço, o n8n consulta a API para listar os barbeiros que oferecem aquele serviço.
4.  **Usuário escolhe barbeiro → n8n chama GET agenda:** Com o barbeiro selecionado, o n8n busca a agenda disponível do barbeiro para a data desejada.
5.  **Usuário escolhe horário → n8n faz POST /agendamentos:** O n8n envia uma requisição POST para a API, criando o agendamento com base nas escolhas do usuário.
6.  **Sistema envia confirmação por WhatsApp:** Após a criação bem-sucedida do agendamento, o sistema (via n8n) envia uma mensagem de confirmação ao usuário no WhatsApp.




## 4. Requisitos Não Funcionais

### 4.1. Segurança

A segurança é um pilar fundamental do sistema BarberFlow. Serão implementadas as seguintes medidas:

-   **Criptografia de Senhas:** Todas as senhas de usuários serão armazenadas de forma segura, utilizando algoritmos de hash robustos como o bcrypt, garantindo que mesmo em caso de violação de dados, as senhas não sejam expostas em texto claro.
-   **Autenticação via JWT (JSON Web Tokens):** A autenticação de usuários na API será realizada através de JWTs, proporcionando um método seguro e escalável para verificar a identidade dos usuários e controlar o acesso aos recursos protegidos.
-   **Rate Limiting na API:** Para prevenir ataques de força bruta e abuso da API, será implementado um mecanismo de rate limiting, que limitará o número de requisições que um cliente pode fazer em um determinado período de tempo.
-   **Prevenção de Agendamentos Duplicados:** O sistema terá validações para evitar que agendamentos sejam criados em horários já ocupados ou que um mesmo cliente agende o mesmo serviço com o mesmo barbeiro em horários conflitantes.




### 4.2. Mobile-Ready

O sistema será projetado com uma abordagem "mobile-first", garantindo que todas as interfaces sejam totalmente responsivas e ofereçam uma excelente experiência de usuário em dispositivos móveis (smartphones e tablets). A possibilidade de desenvolver como um PWA (Progressive Web App) será avaliada para oferecer funcionalidades offline e acesso rápido.

### 4.3. Relatórios e Insights

O sistema fornecerá um conjunto abrangente de relatórios e métricas para auxiliar a gestão da barbearia na tomada de decisões estratégicas. Os principais relatórios incluirão:

-   **Faturamento Diário/Mensal:** Análise da receita gerada por período.
-   **Barbeiros Mais Produtivos:** Identificação dos barbeiros com maior volume de atendimentos e faturamento.
-   **Serviços Mais Vendidos:** Ranking dos serviços mais procurados pelos clientes.
-   **Estoque Baixo:** Alertas e listagem de produtos com estoque abaixo do nível mínimo.
-   **Cancelamentos por Cliente:** Análise do comportamento de cancelamento de agendamentos por cliente.




## 5. Arquitetura do Sistema e Tecnologias Sugeridas

Para o desenvolvimento do BarberFlow, propõe-se uma arquitetura de microsserviços ou monolito modular, dependendo da complexidade e escalabilidade futura desejada. No entanto, para a primeira versão, um monolito modular com uma clara separação entre frontend e backend (arquitetura de API-first) é o mais adequado para agilizar o desenvolvimento e manter a complexidade gerenciável.

### 5.1. Arquitetura

-   **Frontend:** Aplicação Single Page Application (SPA) ou Progressive Web App (PWA) que se comunica com o backend via API RESTful.
-   **Backend:** API RESTful que expõe os endpoints para o frontend e para integrações externas (n8n).
-   **Banco de Dados:** Banco de dados relacional para persistência dos dados.

### 5.2. Tecnologias Sugeridas

Considerando as melhores práticas de mercado, a facilidade de desenvolvimento e a escalabilidade, as seguintes tecnologias são sugeridas:

#### Backend
-   **Linguagem:** Python
-   **Framework:** Flask (leve, flexível e ideal para APIs RESTful) ou FastAPI (para alta performance e validação de dados automática).
-   **Banco de Dados:** PostgreSQL (robusto, escalável e amplamente utilizado em aplicações web).
-   **ORM (Object-Relational Mapper):** SQLAlchemy (para interação com o banco de dados de forma orientada a objetos).
-   **Autenticação:** PyJWT (para JWT) e Bcrypt (para hash de senhas).

#### Frontend
-   **Framework/Biblioteca:** React (para construir interfaces de usuário interativas e reativas).
-   **Gerenciamento de Estado:** Redux ou Context API (para gerenciar o estado da aplicação de forma eficiente).
-   **Estilização:** Tailwind CSS (para um desenvolvimento rápido e flexível de UI) ou Styled Components.
-   **Requisições HTTP:** Axios ou Fetch API.

#### Integração e Automação
-   **Plataforma de Automação:** n8n (conforme especificado nos requisitos).

#### Infraestrutura (Implantação)
-   **Servidor Web:** Nginx (para servir o frontend e atuar como proxy reverso para o backend).
-   **Contêineres:** Docker (para empacotar a aplicação e suas dependências, facilitando a implantação e escalabilidade).
-   **Orquestração (futuro):** Kubernetes (para orquestração de contêineres em ambientes de produção de alta escala).

## 6. Cronograma de Alto Nível

O desenvolvimento do BarberFlow será dividido em fases, com entregas incrementais. Abaixo, um cronograma de alto nível:

-   **Fase 1: Análise e Planejamento Detalhado (1 semana)**
    -   Revisão e detalhamento dos requisitos.
    -   Definição da arquitetura e tecnologias.
    -   Criação dos modelos de dados.

-   **Fase 2: Desenvolvimento do Backend (4-6 semanas)**
    -   Configuração do ambiente de desenvolvimento.
    -   Implementação da API RESTful (autenticação, CRUD de usuários, serviços, barbeiros, agendamentos, produtos, finanças).
    -   Testes unitários e de integração do backend.

-   **Fase 3: Desenvolvimento do Frontend (4-6 semanas)**
    -   Configuração do ambiente de desenvolvimento.
    -   Criação das interfaces de usuário (Painel do Cliente, Barbeiro, Administrador).
    -   Integração do frontend com a API do backend.
    -   Testes de usabilidade e responsividade.

-   **Fase 4: Integrações e Segurança (2-3 semanas)**
    -   Implementação da integração com n8n para WhatsApp.
    -   Reforço das medidas de segurança (rate limiting, prevenção de duplicidade).
    -   Desenvolvimento dos relatórios e dashboards.

-   **Fase 5: Testes e Implantação (2 semanas)**
    -   Testes de sistema e aceitação do usuário.
    -   Correção de bugs.
    -   Preparação para implantação em ambiente de produção.
    -   Documentação final.

Este cronograma é uma estimativa e pode ser ajustado conforme a complexidade e os desafios encontrados durante o desenvolvimento.




## 7. Entrega Final Esperada

Ao final do desenvolvimento, o sistema BarberFlow deverá ser um produto funcional e completo, atendendo a todos os requisitos especificados. A entrega final incluirá:

-   **Painel Web Completo:** Interfaces de usuário funcionais e responsivas para clientes, barbeiros e administradores.
-   **Banco de Dados Relacional:** Um banco de dados PostgreSQL populado com o esquema definido e dados de teste.
-   **API Documentada:** Uma API RESTful completa, com autenticação JWT e todos os endpoints especificados, acompanhada de documentação clara (ex: Swagger/OpenAPI).
-   **Integração via n8n:** Demonstração da automação de agendamentos e comunicação via WhatsApp utilizando o n8n.
-   **Dashboard Gerencial:** Um painel de controle para administradores com KPIs e relatórios essenciais para a gestão da barbearia.

Este documento servirá como a base para o desenvolvimento do BarberFlow, garantindo que todas as partes interessadas tenham um entendimento comum dos objetivos e funcionalidades do sistema.


