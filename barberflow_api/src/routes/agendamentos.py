from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, Agendamento, Usuario, Barbeiro, Servico
from datetime import datetime, date, time

agendamentos_bp = Blueprint('agendamentos', __name__)

@agendamentos_bp.route('/', methods=['POST'])
@jwt_required()
def create_agendamento():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        required_fields = ['barbeiro_id', 'servico_id', 'data', 'hora']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        # Verificar se barbeiro e serviço existem
        barbeiro = Barbeiro.query.get(data['barbeiro_id'])
        if not barbeiro:
            return jsonify({'error': 'Barbeiro não encontrado'}), 404
        
        servico = Servico.query.get(data['servico_id'])
        if not servico:
            return jsonify({'error': 'Serviço não encontrado'}), 404
        
        # Converter data e hora
        try:
            data_agendamento = datetime.strptime(data['data'], '%Y-%m-%d').date()
            hora_agendamento = datetime.strptime(data['hora'], '%H:%M').time()
        except ValueError:
            return jsonify({'error': 'Formato de data/hora inválido'}), 400
        
        # Verificar se o horário está disponível para o barbeiro
        agendamento_existente = Agendamento.query.filter(
            Agendamento.barbeiro_id == data["barbeiro_id"],
            Agendamento.data == data_agendamento,
            Agendamento.hora == hora_agendamento,
            Agendamento.status.in_(["pendente", "confirmado"])
        ).first()
        
        if agendamento_existente:
            return jsonify({"error": "Horário já ocupado para este barbeiro"}), 409
        
        agendamento = Agendamento(
            cliente_id=current_user_id,
            barbeiro_id=data['barbeiro_id'],
            servico_id=data['servico_id'],
            data=data_agendamento,
            hora=hora_agendamento,
            valor_final=data.get('valor_final', servico.preco),
            forma_pagamento=data.get('forma_pagamento')
        )
        
        db.session.add(agendamento)
        db.session.commit()
        
        return jsonify({
            'message': 'Agendamento criado com sucesso',
            'agendamento': agendamento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agendamentos_bp.route('/cliente/<int:cliente_id>', methods=['GET'])
@jwt_required()
def get_agendamentos_cliente(cliente_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        # Verificar permissões
        if current_user.tipo != 'gerente' and current_user_id != cliente_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        agendamentos = Agendamento.query.filter_by(cliente_id=cliente_id).order_by(
            Agendamento.data.desc(), Agendamento.hora.desc()
        ).all()
        
        return jsonify([agendamento.to_dict() for agendamento in agendamentos]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agendamentos_bp.route('/<int:agendamento_id>', methods=['PATCH'])
@jwt_required()
def update_agendamento(agendamento_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        agendamento = Agendamento.query.get(agendamento_id)
        if not agendamento:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
        
        # Verificar permissões
        is_owner = current_user_id == agendamento.cliente_id
        is_barbeiro = current_user.tipo == 'barbeiro' and current_user.barbeiro and current_user.barbeiro.id == agendamento.barbeiro_id
        is_gerente = current_user.tipo == 'gerente'
        
        if not (is_owner or is_barbeiro or is_gerente):
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        # Atualizar campos permitidos
        if 'status' in data:
            if data['status'] not in ['pendente', 'confirmado', 'realizado', 'cancelado']:
                return jsonify({'error': 'Status inválido'}), 400
            agendamento.status = data['status']
        
        if 'valor_final' in data and (is_barbeiro or is_gerente):
            agendamento.valor_final = data['valor_final']
        
        if 'forma_pagamento' in data and (is_barbeiro or is_gerente):
            agendamento.forma_pagamento = data['forma_pagamento']
        
        # Reagendamento (apenas cliente ou gerente)
        if ('data' in data or 'hora' in data) and (is_owner or is_gerente):
            if agendamento.status in ['realizado', 'cancelado']:
                return jsonify({'error': 'Não é possível reagendar agendamento realizado ou cancelado'}), 400
            
            nova_data = agendamento.data
            nova_hora = agendamento.hora
            
            if 'data' in data:
                try:
                    nova_data = datetime.strptime(data['data'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'error': 'Formato de data inválido'}), 400
            
            if 'hora' in data:
                try:
                    nova_hora = datetime.strptime(data['hora'], '%H:%M').time()
                except ValueError:
                    return jsonify({'error': 'Formato de hora inválido'}), 400
            
            # Verificar se o novo horário está disponível
            if nova_data != agendamento.data or nova_hora != agendamento.hora:
                agendamento_existente = Agendamento.query.filter_by(
                    barbeiro_id=agendamento.barbeiro_id,
                    data=nova_data,
                    hora=nova_hora
                ).filter(Agendamento.id != agendamento_id).first()
                
                if agendamento_existente:
                    return jsonify({'error': 'Novo horário já ocupado'}), 409
                
                agendamento.data = nova_data
                agendamento.hora = nova_hora
        
        db.session.commit()
        
        return jsonify({
            'message': 'Agendamento atualizado com sucesso',
            'agendamento': agendamento.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@agendamentos_bp.route('/', methods=['GET'])
@jwt_required()
def get_agendamentos():
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo == 'gerente':
            # Gerente vê todos os agendamentos
            agendamentos = Agendamento.query.order_by(
                Agendamento.data.desc(), Agendamento.hora.desc()
            ).all()
        elif current_user.tipo == 'barbeiro' and current_user.barbeiro:
            # Barbeiro vê apenas seus agendamentos
            agendamentos = Agendamento.query.filter_by(
                barbeiro_id=current_user.barbeiro.id
            ).order_by(Agendamento.data.desc(), Agendamento.hora.desc()).all()
        else:
            # Cliente vê apenas seus agendamentos
            agendamentos = Agendamento.query.filter_by(
                cliente_id=current_user_id
            ).order_by(Agendamento.data.desc(), Agendamento.hora.desc()).all()
        
        return jsonify([agendamento.to_dict() for agendamento in agendamentos]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

