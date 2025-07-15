# Guia de Integração BarberFlow + n8n + WhatsApp

## Visão Geral

Este guia explica como integrar o sistema BarberFlow com n8n para automatizar o atendimento via WhatsApp, permitindo que clientes façam agendamentos, consultem informações e recebam notificações diretamente pelo WhatsApp.

## Arquitetura da Integração

```
WhatsApp Business API → n8n → BarberFlow API → Banco de Dados
                     ↑                    ↓
                  Webhook              Resposta
```

## Configuração do n8n

### 1. Instalação do n8n

```bash
# Via Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Via npm
npm install n8n -g
n8n start
```

### 2. Configuração do WhatsApp Business API

Para conectar o WhatsApp ao n8n, você precisará:

1. **WhatsApp Business Account**
2. **Facebook Developer Account**
3. **Webhook URL configurada**

#### Configuração do Webhook no n8n:

1. Crie um novo workflow no n8n
2. Adicione um nó "Webhook"
3. Configure a URL: `http://seu-n8n.com/webhook/whatsapp`
4. Método: POST
5. Configure no Facebook Developer Console

### 3. Fluxos de Automação

#### Fluxo 1: Recebimento de Mensagens WhatsApp

```json
{
  "nodes": [
    {
      "name": "WhatsApp Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "whatsapp",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Process Message",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Extrair dados da mensagem\nconst message = items[0].json;\nconst phoneNumber = message.from;\nconst text = message.text.body;\nconst senderName = message.profile?.name || 'Cliente';\n\nreturn [{\n  json: {\n    phone_number: phoneNumber,\n    message: text,\n    name: senderName\n  }\n}];"
      }
    },
    {
      "name": "BarberFlow API",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://sua-api.com/webhooks/whatsapp",
        "method": "POST",
        "body": "json",
        "jsonBody": "={{ $json }}"
      }
    },
    {
      "name": "Send WhatsApp Response",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://graph.facebook.com/v17.0/PHONE_NUMBER_ID/messages",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer YOUR_ACCESS_TOKEN",
          "Content-Type": "application/json"
        },
        "body": "json",
        "jsonBody": "={\n  \"messaging_product\": \"whatsapp\",\n  \"to\": \"{{ $('Process Message').item.json.phone_number }}\",\n  \"text\": {\n    \"body\": \"{{ $('BarberFlow API').item.json.response }}\"\n  }\n}"
      }
    }
  ]
}
```

#### Fluxo 2: Agendamento via WhatsApp

```json
{
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "schedule",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Create Appointment",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://sua-api.com/webhooks/n8n/agendamento",
        "method": "POST",
        "body": "json",
        "jsonBody": "={{ $json }}"
      }
    },
    {
      "name": "Send Confirmation",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://graph.facebook.com/v17.0/PHONE_NUMBER_ID/messages",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer YOUR_ACCESS_TOKEN"
        },
        "body": "json",
        "jsonBody": "={\n  \"messaging_product\": \"whatsapp\",\n  \"to\": \"{{ $json.phone_number }}\",\n  \"text\": {\n    \"body\": \"{{ $('Create Appointment').item.json.response_message }}\"\n  }\n}"
      }
    }
  ]
}
```

#### Fluxo 3: Notificações Automáticas

```json
{
  "nodes": [
    {
      "name": "Schedule Reminder",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "triggerTimes": {
          "hour": 9,
          "minute": 0
        }
      }
    },
    {
      "name": "Get Tomorrow Appointments",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://sua-api.com/api/agendamentos?data={{ $now.plus({days: 1}).toFormat('yyyy-MM-dd') }}",
        "method": "GET",
        "headers": {
          "Authorization": "Bearer YOUR_API_TOKEN"
        }
      }
    },
    {
      "name": "Send Reminders",
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": {
        "batchSize": 1
      }
    },
    {
      "name": "WhatsApp Reminder",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://graph.facebook.com/v17.0/PHONE_NUMBER_ID/messages",
        "method": "POST",
        "headers": {
          "Authorization": "Bearer YOUR_ACCESS_TOKEN"
        },
        "body": "json",
        "jsonBody": "={\n  \"messaging_product\": \"whatsapp\",\n  \"to\": \"{{ $json.cliente.telefone }}\",\n  \"text\": {\n    \"body\": \"🔔 Lembrete: Você tem um agendamento amanhã às {{ $json.hora }} com {{ $json.barbeiro.nome }}. Confirme sua presença!\"\n  }\n}"
      }
    }
  ]
}
```

## Endpoints da API BarberFlow

### 1. Webhook Principal
- **URL:** `/webhooks/whatsapp`
- **Método:** POST
- **Descrição:** Processa mensagens recebidas do WhatsApp

**Payload:**
```json
{
  "from": "5511999999999",
  "message": "menu",
  "name": "João Silva"
}
```

**Resposta:**
```json
{
  "success": true,
  "response": "🔹 BARBERFLOW - MENU PRINCIPAL 🔹\n\nOlá! Bem-vindo...",
  "phone": "5511999999999"
}
```

### 2. Criar Agendamento via n8n
- **URL:** `/webhooks/n8n/agendamento`
- **Método:** POST
- **Descrição:** Cria agendamento através do n8n

**Payload:**
```json
{
  "phone_number": "5511999999999",
  "cliente_nome": "João Silva",
  "barbeiro_nome": "Carlos",
  "servico_nome": "Corte Masculino",
  "data": "2024-01-15",
  "hora": "14:30"
}
```

### 3. Atualizar Status
- **URL:** `/webhooks/n8n/status/{agendamento_id}`
- **Método:** PATCH
- **Descrição:** Atualiza status do agendamento

**Payload:**
```json
{
  "status": "confirmado"
}
```

### 4. Enviar Notificação
- **URL:** `/webhooks/n8n/notifications`
- **Método:** POST
- **Descrição:** Envia notificação personalizada

**Payload:**
```json
{
  "phone_number": "5511999999999",
  "message": "Sua mensagem personalizada aqui"
}
```

## Comandos WhatsApp Disponíveis

| Comando | Descrição |
|---------|-----------|
| `menu` ou `ajuda` | Exibe menu principal |
| `agendar` | Informações sobre agendamento |
| `serviços` | Lista serviços e preços |
| `barbeiros` | Lista equipe de barbeiros |
| `horários` | Horários de funcionamento |
| `meus agendamentos` | Consulta agendamentos do cliente |
| `cancelar` | Informações sobre cancelamento |
| `contato` | Informações de contato |
| `endereço` | Localização da barbearia |

## Configuração de Variáveis de Ambiente

No n8n, configure as seguintes variáveis:

```env
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
BARBERFLOW_API_URL=http://sua-api.com
BARBERFLOW_API_TOKEN=your_api_token
```

## Fluxo de Agendamento Completo

1. **Cliente envia mensagem:** "Quero agendar"
2. **n8n processa:** Envia para BarberFlow API
3. **API responde:** Menu de opções
4. **Cliente escolhe:** Serviço, barbeiro, data/hora
5. **n8n cria agendamento:** Via endpoint específico
6. **Confirmação automática:** Mensagem de sucesso
7. **Lembrete automático:** 24h antes do agendamento

## Monitoramento e Logs

### Logs no n8n
- Acesse a interface do n8n
- Vá em "Executions" para ver histórico
- Configure alertas para falhas

### Logs na API BarberFlow
- Logs são salvos automaticamente
- Monitore endpoints `/webhooks/*`
- Configure alertas para erros 500

## Troubleshooting

### Problemas Comuns

1. **Webhook não recebe mensagens**
   - Verifique URL no Facebook Developer
   - Confirme que n8n está acessível
   - Teste com ngrok para desenvolvimento

2. **API não responde**
   - Verifique se BarberFlow está rodando
   - Confirme endpoints estão corretos
   - Teste com Postman/curl

3. **Mensagens não são enviadas**
   - Verifique token do WhatsApp
   - Confirme Phone Number ID
   - Teste permissões da conta Business

### Comandos de Teste

```bash
# Testar webhook
curl -X POST http://localhost:5678/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"from": "5511999999999", "message": "menu", "name": "Teste"}'

# Testar agendamento
curl -X POST http://localhost:5001/webhooks/n8n/agendamento \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "5511999999999",
    "cliente_nome": "João Teste",
    "barbeiro_nome": "Carlos",
    "servico_nome": "Corte",
    "data": "2024-01-15",
    "hora": "14:30"
  }'
```

## Segurança

1. **Autenticação:** Use tokens seguros
2. **HTTPS:** Sempre em produção
3. **Rate Limiting:** Já implementado na API
4. **Validação:** Todos os inputs são validados
5. **Logs:** Monitore tentativas suspeitas

## Próximos Passos

1. Configure conta WhatsApp Business
2. Instale e configure n8n
3. Importe workflows fornecidos
4. Configure variáveis de ambiente
5. Teste fluxos básicos
6. Implante em produção
7. Configure monitoramento

## Suporte

Para dúvidas sobre a integração:
- Email: suporte@barberflow.com
- Documentação: [Link para docs]
- Issues: [Link para GitHub]

