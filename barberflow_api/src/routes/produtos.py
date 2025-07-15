from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, Produto, VendaProduto, Usuario

produtos_bp = Blueprint('produtos', __name__)

@produtos_bp.route('/', methods=['GET'])
def get_produtos():
    try:
        tipo_filtro = request.args.get('tipo')
        
        if tipo_filtro:
            if tipo_filtro not in ['venda', 'uso_interno']:
                return jsonify({'error': 'Tipo inválido'}), 400
            produtos = Produto.query.filter_by(tipo=tipo_filtro).all()
        else:
            produtos = Produto.query.all()
        
        return jsonify([produto.to_dict() for produto in produtos]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@produtos_bp.route('/<int:produto_id>', methods=['GET'])
def get_produto(produto_id):
    try:
        produto = Produto.query.get(produto_id)
        if not produto:
            return jsonify({'error': 'Produto não encontrado'}), 404
        
        return jsonify(produto.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@produtos_bp.route('/', methods=['POST'])
@jwt_required()
def create_produto():
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo != 'gerente':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        required_fields = ['nome', 'tipo', 'quantidade']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        if data['tipo'] not in ['venda', 'uso_interno']:
            return jsonify({'error': 'Tipo inválido'}), 400
        
        produto = Produto(
            nome=data['nome'],
            tipo=data['tipo'],
            quantidade=data['quantidade'],
            unidade=data.get('unidade'),
            custo_unitario=data.get('custo_unitario'),
            preco_venda=data.get('preco_venda')
        )
        
        db.session.add(produto)
        db.session.commit()
        
        return jsonify({
            'message': 'Produto criado com sucesso',
            'produto': produto.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@produtos_bp.route('/<int:produto_id>', methods=['PUT'])
@jwt_required()
def update_produto(produto_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo != 'gerente':
            return jsonify({'error': 'Acesso negado'}), 403
        
        produto = Produto.query.get(produto_id)
        if not produto:
            return jsonify({'error': 'Produto não encontrado'}), 404
        
        data = request.get_json()
        
        if 'nome' in data:
            produto.nome = data['nome']
        if 'tipo' in data:
            if data['tipo'] not in ['venda', 'uso_interno']:
                return jsonify({'error': 'Tipo inválido'}), 400
            produto.tipo = data['tipo']
        if 'quantidade' in data:
            produto.quantidade = data['quantidade']
        if 'unidade' in data:
            produto.unidade = data['unidade']
        if 'custo_unitario' in data:
            produto.custo_unitario = data['custo_unitario']
        if 'preco_venda' in data:
            produto.preco_venda = data['preco_venda']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Produto atualizado com sucesso',
            'produto': produto.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@produtos_bp.route('/vendas', methods=['POST'])
@jwt_required()
def create_venda_produto():
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo not in ['barbeiro', 'gerente']:
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        required_fields = ['produto_id', 'quantidade', 'valor_total']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        produto = Produto.query.get(data['produto_id'])
        if not produto:
            return jsonify({'error': 'Produto não encontrado'}), 404
        
        if produto.tipo != 'venda':
            return jsonify({'error': 'Produto não é para venda'}), 400
        
        if produto.quantidade < data['quantidade']:
            return jsonify({'error': 'Estoque insuficiente'}), 400
        
        venda = VendaProduto(
            produto_id=data['produto_id'],
            cliente_id=data.get('cliente_id'),
            quantidade=data['quantidade'],
            valor_total=data['valor_total']
        )
        
        # Atualizar estoque
        produto.quantidade -= data['quantidade']
        
        db.session.add(venda)
        db.session.commit()
        
        return jsonify({
            'message': 'Venda registrada com sucesso',
            'venda': venda.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@produtos_bp.route('/vendas', methods=['GET'])
@jwt_required()
def get_vendas():
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo != 'gerente':
            return jsonify({'error': 'Acesso negado'}), 403
        
        vendas = VendaProduto.query.order_by(VendaProduto.data.desc()).all()
        
        return jsonify([venda.to_dict() for venda in vendas]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

