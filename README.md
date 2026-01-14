<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=250&section=header&text=BARBERFLOW&fontSize=60&fontAlignY=35&desc=SaaS%20Vertical%20|%20Gestão%20Inteligente%20de%20Fluxo&descAlignY=55&descSize=18&fontColor=ffffff&customColorList=06b6d4,000205&animation=fadeIn" width="100%"/>
</div>

<div align="center">
  <br />
  
  <a href="https://github.com/RomarioDelphin">
    <img src="https://img.shields.io/badge/DEV-ROMARIO%20DELPHIN-000205?style=for-the-badge&logo=github&logoColor=06b6d4&labelColor=000205&color=06b6d4" />
  </a>
  <img src="https://img.shields.io/badge/STATUS-EM%20PRODUÇÃO-000205?style=for-the-badge&logo=react&logoColor=00ff9d&labelColor=000205&color=00ff9d" />
  <img src="https://img.shields.io/badge/INTEGRAÇÃO-N8N%20READY-000205?style=for-the-badge&logo=n8n&logoColor=ff6b6b&labelColor=000205&color=ff6b6b" />

</div>

<br />

## ⚡ Sobre o Projeto (Business Logic)

O **BarberFlow** é uma solução full-stack de agendamento e gestão de serviços, projetada como uma implementação vertical da arquitetura **HumanDesk**. 

Diferente de agendas comuns, este sistema foi arquitetado para ser **Data-Driven**, utilizando containers Docker para orquestração e pronto para integração com automações de IA via **n8n** para disparos de confirmação e retenção de clientes (CRM).

### 🎯 Funcionalidades Core
* **Gestão de Agenda Real-Time:** Backend otimizado para alta concorrência.
* **Arquitetura Containerizada:** Deploy escalável via `Docker Compose`.
* **API Restful:** Comunicação desacoplada entre Frontend e Backend.
* **Automação (n8n):** Webhooks preparados para integração com disparos de WhatsApp/Email.

---

## 🛠️ Tech Stack & Arquitetura

O projeto utiliza uma stack moderna focada em performance e escalabilidade:

<div align="center">
  <img src="https://skillicons.dev/icons?i=js,react,python,flask,postgres,docker,n8n,linux&perline=10" />
</div>

| Componente | Tecnologia | Descrição |
| :--- | :--- | :--- |
| **Frontend** | `JavaScript / React` | Interface reativa e experiência do usuário (UX). |
| **Backend** | `Python / Flask` | Lógica de negócios e endpoints de API. |
| **Database** | `PostgreSQL / SQL` | Modelagem relacional robusta (`schema.sql`). |
| **DevOps** | `Docker` | Ambiente padronizado e deploy via `docker-compose`. |
| **Automação** | `n8n` | Orquestração de fluxos de mensagem e CRM. |

---

## 📂 Estrutura do Repositório

```bash
barberflow/
├── 🐳 docker-compose.yml       # Orquestração dos containers (App + DB)
├── 🔌 barberflow_api/          # Backend (Python/Flask)
├── 🎨 front-end/               # Interface do Usuário
├── 📜 barberflow_schema.sql    # Estrutura do Banco de Dados
├── 🤖 n8n_integration_guide.md # Documentação de Automação
└── 📄 analise_requisitos.md    # Engenharia de Software
