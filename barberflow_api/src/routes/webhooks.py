from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, Usuario, Barbeiro, Servico, Agendamento
from datetime import datetime, date, time
import json
import re

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """
    Webhook para receber mensagens do WhatsApp via n8n
    """
    try:
        data = request.get_json()
        
        # Extrair informações da mensagem
        phone_number = data.get('from', '').replace('+', '').replace(' ', '')
        message = data.get('message', '').lower().strip()
        sender_name = data.get('name', 'Cliente')
        
        # Processar comando
        response = process_whatsapp_message(phone_number, message, sender_name)
        
        return jsonify({
            'success': True,
            'response': response,
            'phone': phone_number
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def process_whatsapp_message(phone_number, message, sender_name):
    """
    Processa mensagens do WhatsApp e retorna resposta apropriada
    """
    
    # Comandos disponíveis
    if 'menu' in message or 'ajuda' in message or message == 'oi' or message == 'olá':
        return get_menu_message()
    
    elif 'agendar' in message or 'agendamento' in message:
        return get_scheduling_info()
    
    elif 'servicos' in message or 'serviços' in message:
        return get_services_list()
    
    elif 'barbeiros' in message:
        return get_barbers_list()
    
    elif 'horarios' in message or 'horários' in message:
        return get_available_times()
    
    elif 'cancelar' in message:
        return get_cancellation_info(phone_number)
    
    elif 'meus agendamentos' in message or 'agendamentos' in message:
        return get_user_appointments(phone_number)
    
    elif 'contato' in message or 'telefone' in message:
        return get_contact_info()
    
    elif 'endereco' in message or 'endereço' in message or 'localização' in message:
        return get_location_info()
    
    else:
        return get_default_response()

def get_menu_message():
    """Retorna o menu principal"""
    return """🔹 *BARBERFLOW - MENU PRINCIPAL* 🔹

Olá! Bem-vindo ao nosso sistema de agendamento! 

📋 *Comandos disponíveis:*

• *AGENDAR* - Fazer um novo agendamento
• *SERVIÇOS* - Ver lista de serviços e preços
• *BARBEIROS* - Conhecer nossa equipe
• *HORÁRIOS* - Ver horários disponíveis
• *MEUS AGENDAMENTOS* - Ver seus agendamentos
• *CANCELAR* - Cancelar um agendamento
• *CONTATO* - Informações de contato
• *ENDEREÇO* - Nossa localização

Digite qualquer comando para começar! 💈"""

def get_scheduling_info():
    """Retorna informações sobre agendamento"""
    return """📅 *COMO AGENDAR*

Para fazer seu agendamento, você pode:

1️⃣ *Pelo WhatsApp:* 
   • Digite "SERVIÇOS" para ver opções
   • Digite "BARBEIROS" para escolher
   • Digite "HORÁRIOS" para ver disponibilidade

2️⃣ *Pelo Site:* 
   • Acesse nosso sistema online
   • Faça login ou cadastre-se
   • Escolha serviço, barbeiro e horário

3️⃣ *Por Telefone:*
   • Ligue para (11) 99999-9999
   • Fale diretamente conosco

⚠️ *Importante:* Agendamentos pelo WhatsApp precisam ser confirmados por nossa equipe.

Digite *MENU* para voltar ao início."""

def get_services_list():
    """Retorna lista de serviços"""
    try:
        servicos = Servico.query.filter_by(ativo=True).all()
        
        if not servicos:
            return "Desculpe, não há serviços disponíveis no momento."
        
        message = "💈 *NOSSOS SERVIÇOS*\n\n"
        
        for servico in servicos:
            message += f"• *{servico.nome}*\n"
            if servico.descricao:
                message += f"  {servico.descricao}\n"
            message += f"  💰 R$ {servico.preco:.2f}\n"
            message += f"  ⏱️ {servico.duracao} min\n\n"
        
        message += "Para agendar, digite *AGENDAR*\n"
        message += "Digite *MENU* para voltar ao início."
        
        return message
        
    except Exception as e:
        return "Erro ao buscar serviços. Tente novamente mais tarde."

def get_barbers_list():
    """Retorna lista de barbeiros"""
    try:
        barbeiros = Barbeiro.query.filter_by(ativo=True).all()
        
        if not barbeiros:
            return "Desculpe, não há barbeiros disponíveis no momento."
        
        message = "👨‍💼 *NOSSA EQUIPE*\n\n"
        
        for barbeiro in barbeiros:
            usuario = Usuario.query.get(barbeiro.usuario_id)
            message += f"• *{usuario.nome}*\n"
            if barbeiro.especialidades:
                message += f"  Especialidades: {barbeiro.especialidades}\n"
            message += f"  Comissão: {barbeiro.percentual_comissao}%\n\n"
        
        message += "Para agendar com um barbeiro específico, digite *AGENDAR*\n"
        message += "Digite *MENU* para voltar ao início."
        
        return message
        
    except Exception as e:
        return "Erro ao buscar barbeiros. Tente novamente mais tarde."

def get_available_times():
    """Retorna horários disponíveis (genérico)"""
    return """🕐 *HORÁRIOS DE FUNCIONAMENTO*

*Segunda a Sexta:* 9h às 19h
*Sábado:* 8h às 17h
*Domingo:* Fechado

⏰ *Horários de Agendamento:*
• De 30 em 30 minutos
• Último agendamento: 1h antes do fechamento

📱 Para ver horários específicos disponíveis, acesse nosso sistema online ou ligue para (11) 99999-9999.

Digite *AGENDAR* para fazer seu agendamento
Digite *MENU* para voltar ao início."""

def get_cancellation_info(phone_number):
    """Retorna informações sobre cancelamento"""
    try:
        # Buscar usuário pelo telefone
        usuario = Usuario.query.filter_by(telefone=phone_number).first()
        
        if not usuario:
            return """❌ *CANCELAMENTO*

Para cancelar um agendamento, você precisa:

1️⃣ Estar cadastrado em nosso sistema
2️⃣ Ter agendamentos ativos

📱 Acesse nosso sistema online para fazer login ou cadastro.
📞 Ou ligue para (11) 99999-9999

Digite *MENU* para voltar ao início."""
        
        # Buscar agendamentos ativos
        agendamentos = Agendamento.query.filter(
            Agendamento.cliente_id == usuario.id,
            Agendamento.status.in_(['pendente', 'confirmado'])
        ).all()
        
        if not agendamentos:
            return """✅ *CANCELAMENTO*

Você não possui agendamentos ativos para cancelar.

Digite *AGENDAR* para fazer um novo agendamento
Digite *MENU* para voltar ao início."""
        
        message = "❌ *SEUS AGENDAMENTOS ATIVOS*\n\n"
        
        for agendamento in agendamentos:
            barbeiro = Barbeiro.query.get(agendamento.barbeiro_id)
            barbeiro_usuario = Usuario.query.get(barbeiro.usuario_id)
            servico = Servico.query.get(agendamento.servico_id)
            
            message += f"📅 {agendamento.data.strftime('%d/%m/%Y')}\n"
            message += f"🕐 {agendamento.hora.strftime('%H:%M')}\n"
            message += f"💈 {servico.nome}\n"
            message += f"👨‍💼 {barbeiro_usuario.nome}\n"
            message += f"📊 Status: {agendamento.status}\n\n"
        
        message += "📞 Para cancelar, ligue para (11) 99999-9999\n"
        message += "💻 Ou acesse nosso sistema online\n\n"
        message += "Digite *MENU* para voltar ao início."
        
        return message
        
    except Exception as e:
        return "Erro ao buscar agendamentos. Tente novamente mais tarde."

def get_user_appointments(phone_number):
    """Retorna agendamentos do usuário"""
    try:
        # Buscar usuário pelo telefone
        usuario = Usuario.query.filter_by(telefone=phone_number).first()
        
        if not usuario:
            return """📅 *MEUS AGENDAMENTOS*

Para ver seus agendamentos, você precisa estar cadastrado em nosso sistema.

📱 Acesse nosso sistema online para fazer login ou cadastro.
📞 Ou ligue para (11) 99999-9999

Digite *MENU* para voltar ao início."""
        
        # Buscar agendamentos do usuário
        agendamentos = Agendamento.query.filter_by(
            cliente_id=usuario.id
        ).order_by(Agendamento.data.desc(), Agendamento.hora.desc()).limit(5).all()
        
        if not agendamentos:
            return """📅 *MEUS AGENDAMENTOS*

Você ainda não possui agendamentos.

Digite *AGENDAR* para fazer seu primeiro agendamento
Digite *MENU* para voltar ao início."""
        
        message = f"📅 *AGENDAMENTOS - {usuario.nome}*\n\n"
        
        for agendamento in agendamentos:
            barbeiro = Barbeiro.query.get(agendamento.barbeiro_id)
            barbeiro_usuario = Usuario.query.get(barbeiro.usuario_id)
            servico = Servico.query.get(agendamento.servico_id)
            
            status_emoji = {
                'pendente': '⏳',
                'confirmado': '✅',
                'realizado': '✅',
                'cancelado': '❌'
            }.get(agendamento.status, '❓')
            
            message += f"{status_emoji} *{agendamento.data.strftime('%d/%m/%Y')} - {agendamento.hora.strftime('%H:%M')}*\n"
            message += f"💈 {servico.nome}\n"
            message += f"👨‍💼 {barbeiro_usuario.nome}\n"
            message += f"📊 {agendamento.status.title()}\n\n"
        
        message += "💻 Para mais detalhes, acesse nosso sistema online\n"
        message += "Digite *MENU* para voltar ao início."
        
        return message
        
    except Exception as e:
        return "Erro ao buscar agendamentos. Tente novamente mais tarde."

def get_contact_info():
    """Retorna informações de contato"""
    return """📞 *CONTATO*

*Telefone:* (11) 99999-9999
*WhatsApp:* (11) 99999-9999
*Email:* contato@barberflow.com

*Horários de Atendimento:*
• Segunda a Sexta: 9h às 19h
• Sábado: 8h às 17h
• Domingo: Fechado

💻 *Sistema Online:* 
Acesse nosso site para agendamentos e mais informações.

Digite *MENU* para voltar ao início."""

def get_location_info():
    """Retorna informações de localização"""
    return """📍 *LOCALIZAÇÃO*

*Endereço:*
Rua das Flores, 123
Centro - São Paulo/SP
CEP: 01234-567

*Referências:*
• Próximo ao Shopping Center
• Em frente à Praça da Matriz
• 2 quadras do metrô

🚗 *Estacionamento:* Disponível na rua
🚌 *Transporte Público:* Linhas 100, 200, 300

💻 Para mais informações, acesse nosso sistema online.

Digite *MENU* para voltar ao início."""

def get_default_response():
    """Resposta padrão para comandos não reconhecidos"""
    return """❓ *COMANDO NÃO RECONHECIDO*

Desculpe, não entendi sua mensagem.

Digite *MENU* para ver todos os comandos disponíveis.

Ou escolha uma das opções:
• *AGENDAR* - Fazer agendamento
• *SERVIÇOS* - Ver serviços
• *CONTATO* - Falar conosco

Estamos aqui para ajudar! 😊"""

@webhooks_bp.route('/n8n/agendamento', methods=['POST'])
def n8n_create_agendamento():
    """
    Endpoint para n8n criar agendamentos via WhatsApp
    """
    try:
        data = request.get_json()
        
        required_fields = ['phone_number', 'barbeiro_nome', 'servico_nome', 'data', 'hora']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        # Buscar ou criar usuário pelo telefone
        phone_number = data['phone_number'].replace('+', '').replace(' ', '')
        usuario = Usuario.query.filter_by(telefone=phone_number).first()
        
        if not usuario:
            # Criar usuário temporário
            usuario = Usuario(
                nome=data.get('cliente_nome', 'Cliente WhatsApp'),
                email=f"whatsapp_{phone_number}@temp.com",
                senha='temp123',
                tipo='cliente',
                telefone=phone_number
            )
            db.session.add(usuario)
            db.session.flush()
        
        # Buscar barbeiro pelo nome
        barbeiro_usuario = Usuario.query.filter(
            Usuario.nome.ilike(f"%{data['barbeiro_nome']}%"),
            Usuario.tipo == 'barbeiro'
        ).first()
        
        if not barbeiro_usuario:
            return jsonify({'error': 'Barbeiro não encontrado'}), 404
        
        barbeiro = Barbeiro.query.filter_by(usuario_id=barbeiro_usuario.id).first()
        if not barbeiro:
            return jsonify({'error': 'Barbeiro não encontrado'}), 404
        
        # Buscar serviço pelo nome
        servico = Servico.query.filter(
            Servico.nome.ilike(f"%{data['servico_nome']}%")
        ).first()
        
        if not servico:
            return jsonify({'error': 'Serviço não encontrado'}), 404
        
        # Converter data e hora
        try:
            data_agendamento = datetime.strptime(data['data'], '%Y-%m-%d').date()
            hora_agendamento = datetime.strptime(data['hora'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Formato de data/hora inválido'}), 400
        
        # Verificar disponibilidade
        agendamento_existente = Agendamento.query.filter(
            Agendamento.barbeiro_id == barbeiro.id,
            Agendamento.data == data_agendamento,
            Agendamento.hora == hora_agendamento,
            Agendamento.status.in_(['pendente', 'confirmado'])
        ).first()
        
        if agendamento_existente:
            return jsonify({'error': 'Horário já ocupado'}), 409
        
        # Criar agendamento
        agendamento = Agendamento(
            cliente_id=usuario.id,
            barbeiro_id=barbeiro.id,
            servico_id=servico.id,
            data=data_agendamento,
            hora=hora_agendamento,
            valor_final=servico.preco,
            status='pendente'
        )
        
        db.session.add(agendamento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Agendamento criado com sucesso',
            'agendamento': agendamento.to_dict(),
            'response_message': f"""✅ *AGENDAMENTO CRIADO*

📅 Data: {data_agendamento.strftime('%d/%m/%Y')}
🕐 Horário: {hora_agendamento.strftime('%H:%M')}
💈 Serviço: {servico.nome}
👨‍💼 Barbeiro: {barbeiro_usuario.nome}
💰 Valor: R$ {servico.preco:.2f}

⏳ Status: Pendente de confirmação

Entraremos em contato para confirmar seu agendamento!"""
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@webhooks_bp.route('/n8n/status/<int:agendamento_id>', methods=['PATCH'])
def n8n_update_agendamento_status(agendamento_id):
    """
    Endpoint para n8n atualizar status de agendamentos
    """
    try:
        agendamento = Agendamento.query.get(agendamento_id)
        if not agendamento:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
        
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Status é obrigatório'}), 400
        
        if data['status'] not in ['pendente', 'confirmado', 'realizado', 'cancelado']:
            return jsonify({'error': 'Status inválido'}), 400
        
        old_status = agendamento.status
        agendamento.status = data['status']
        
        db.session.commit()
        
        # Gerar mensagem de resposta baseada no status
        cliente = Usuario.query.get(agendamento.cliente_id)
        barbeiro = Barbeiro.query.get(agendamento.barbeiro_id)
        barbeiro_usuario = Usuario.query.get(barbeiro.usuario_id)
        servico = Servico.query.get(agendamento.servico_id)
        
        status_messages = {
            'confirmado': f"""✅ *AGENDAMENTO CONFIRMADO*

Olá {cliente.nome}!

Seu agendamento foi confirmado:

📅 Data: {agendamento.data.strftime('%d/%m/%Y')}
🕐 Horário: {agendamento.hora.strftime('%H:%M')}
💈 Serviço: {servico.nome}
👨‍💼 Barbeiro: {barbeiro_usuario.nome}
💰 Valor: R$ {agendamento.valor_final:.2f}

Aguardamos você! 💈""",
            
            'cancelado': f"""❌ *AGENDAMENTO CANCELADO*

Olá {cliente.nome}!

Seu agendamento foi cancelado:

📅 Data: {agendamento.data.strftime('%d/%m/%Y')}
🕐 Horário: {agendamento.hora.strftime('%H:%M')}
💈 Serviço: {servico.nome}

Para reagendar, digite *AGENDAR*""",
            
            'realizado': f"""✅ *ATENDIMENTO CONCLUÍDO*

Obrigado {cliente.nome}!

Seu atendimento foi concluído:

📅 Data: {agendamento.data.strftime('%d/%m/%Y')}
💈 Serviço: {servico.nome}
👨‍💼 Barbeiro: {barbeiro_usuario.nome}

Esperamos você novamente! 💈"""
        }
        
        response_message = status_messages.get(data['status'], 'Status atualizado com sucesso.')
        
        return jsonify({
            'success': True,
            'message': 'Status atualizado com sucesso',
            'old_status': old_status,
            'new_status': data['status'],
            'response_message': response_message,
            'phone_number': cliente.telefone
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@webhooks_bp.route('/n8n/notifications', methods=['POST'])
def n8n_send_notification():
    """
    Endpoint para n8n enviar notificações personalizadas
    """
    try:
        data = request.get_json()
        
        required_fields = ['phone_number', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        return jsonify({
            'success': True,
            'phone_number': data['phone_number'],
            'message': data['message']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

