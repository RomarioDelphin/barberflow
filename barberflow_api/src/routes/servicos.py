from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, Servico, Usuario

servicos_bp = Blueprint('servicos', __name__)

@servicos_bp.route('/', methods=['GET'])
def get_servicos():
    try:
        servicos = Servico.query.all()
        return jsonify([servico.to_dict() for servico in servicos]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servicos_bp.route('/<int:servico_id>', methods=['GET'])
def get_servico(servico_id):
    try:
        servico = Servico.query.get(servico_id)
        if not servico:
            return jsonify({'error': 'Serviço não encontrado'}), 404
        
        return jsonify(servico.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@servicos_bp.route('/', methods=['POST'])
@jwt_required()
def create_servico():
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo != 'gerente':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        required_fields = ['nome', 'preco', 'duracao']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        servico = Servico(
            nome=data['nome'],
            descricao=data.get('descricao'),
            preco=data['preco'],
            duracao=data['duracao']
        )
        
        db.session.add(servico)
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço criado com sucesso',
            'servico': servico.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servicos_bp.route('/<int:servico_id>', methods=['PUT'])
@jwt_required()
def update_servico(servico_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo != 'gerente':
            return jsonify({'error': 'Acesso negado'}), 403
        
        servico = Servico.query.get(servico_id)
        if not servico:
            return jsonify({'error': 'Serviço não encontrado'}), 404
        
        data = request.get_json()
        
        if 'nome' in data:
            servico.nome = data['nome']
        if 'descricao' in data:
            servico.descricao = data['descricao']
        if 'preco' in data:
            servico.preco = data['preco']
        if 'duracao' in data:
            servico.duracao = data['duracao']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Serviço atualizado com sucesso',
            'servico': servico.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@servicos_bp.route('/<int:servico_id>', methods=['DELETE'])
@jwt_required()
def delete_servico(servico_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo != 'gerente':
            return jsonify({'error': 'Acesso negado'}), 403
        
        servico = Servico.query.get(servico_id)
        if not servico:
            return jsonify({'error': 'Serviço não encontrado'}), 404
        
        db.session.delete(servico)
        db.session.commit()
        
        return jsonify({'message': 'Serviço excluído com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

