from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, Barbeiro, Usuario, Agendamento
from datetime import datetime, date

barbeiros_bp = Blueprint('barbeiros', __name__)

@barbeiros_bp.route('/', methods=['GET'])
def get_barbeiros():
    try:
        barbeiros = Barbeiro.query.all()
        return jsonify([barbeiro.to_dict() for barbeiro in barbeiros]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@barbeiros_bp.route('/<int:barbeiro_id>', methods=['GET'])
def get_barbeiro(barbeiro_id):
    try:
        barbeiro = Barbeiro.query.get(barbeiro_id)
        if not barbeiro:
            return jsonify({'error': 'Barbeiro não encontrado'}), 404
        
        return jsonify(barbeiro.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@barbeiros_bp.route('/', methods=['POST'])
@jwt_required()
def create_barbeiro():
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo != 'gerente':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        required_fields = ['usuario_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        # Verificar se o usuário existe e é do tipo barbeiro
        usuario = Usuario.query.get(data['usuario_id'])
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if usuario.tipo != 'barbeiro':
            return jsonify({'error': 'Usuário deve ser do tipo barbeiro'}), 400
        
        # Verificar se já existe um barbeiro para este usuário
        if Barbeiro.query.filter_by(usuario_id=data['usuario_id']).first():
            return jsonify({'error': 'Barbeiro já cadastrado para este usuário'}), 409
        
        barbeiro = Barbeiro(
            usuario_id=data['usuario_id'],
            especialidades=data.get('especialidades'),
            horario_de_trabalho=data.get('horario_de_trabalho'),
            dias_de_folga=data.get('dias_de_folga')
        )
        
        db.session.add(barbeiro)
        db.session.commit()
        
        return jsonify({
            'message': 'Barbeiro criado com sucesso',
            'barbeiro': barbeiro.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@barbeiros_bp.route('/<int:barbeiro_id>/agenda', methods=['GET'])
def get_agenda_barbeiro(barbeiro_id):
    try:
        barbeiro = Barbeiro.query.get(barbeiro_id)
        if not barbeiro:
            return jsonify({'error': 'Barbeiro não encontrado'}), 404
        
        data_param = request.args.get('data')
        if data_param:
            try:
                data_filtro = datetime.strptime(data_param, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
            
            agendamentos = Agendamento.query.filter_by(
                barbeiro_id=barbeiro_id,
                data=data_filtro
            ).order_by(Agendamento.hora).all()
        else:
            agendamentos = Agendamento.query.filter_by(
                barbeiro_id=barbeiro_id
            ).filter(Agendamento.data >= date.today()).order_by(
                Agendamento.data, Agendamento.hora
            ).all()
        
        return jsonify([agendamento.to_dict() for agendamento in agendamentos]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@barbeiros_bp.route('/<int:barbeiro_id>', methods=['PUT'])
@jwt_required()
def update_barbeiro(barbeiro_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        barbeiro = Barbeiro.query.get(barbeiro_id)
        if not barbeiro:
            return jsonify({'error': 'Barbeiro não encontrado'}), 404
        
        # Verificar permissões
        if current_user.tipo != 'gerente' and current_user_id != barbeiro.usuario_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        if 'especialidades' in data:
            barbeiro.especialidades = data['especialidades']
        if 'horario_de_trabalho' in data:
            barbeiro.horario_de_trabalho = data['horario_de_trabalho']
        if 'dias_de_folga' in data:
            barbeiro.dias_de_folga = data['dias_de_folga']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Barbeiro atualizado com sucesso',
            'barbeiro': barbeiro.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

