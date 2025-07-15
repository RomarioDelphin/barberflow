from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, MovimentacaoFinanceira, Repasse, Usuario, Barbeiro
from datetime import datetime, date
from sqlalchemy import func, extract

financeiro_bp = Blueprint('financeiro', __name__)

@financeiro_bp.route('/fluxo', methods=['GET'])
@jwt_required()
def get_fluxo_caixa():
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo != 'gerente':
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = MovimentacaoFinanceira.query
        
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
                query = query.filter(MovimentacaoFinanceira.data >= data_inicio_obj)
            except ValueError:
                return jsonify({'error': 'Formato de data_inicio inválido'}), 400
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d')
                query = query.filter(MovimentacaoFinanceira.data <= data_fim_obj)
            except ValueError:
                return jsonify({'error': 'Formato de data_fim inválido'}), 400
        
        movimentacoes = query.order_by(MovimentacaoFinanceira.data.desc()).all()
        
        # Calcular totais
        total_entradas = sum(m.valor for m in movimentacoes if m.tipo == 'entrada')
        total_saidas = sum(m.valor for m in movimentacoes if m.tipo == 'saida')
        saldo = total_entradas - total_saidas
        
        return jsonify({
            'movimentacoes': [mov.to_dict() for mov in movimentacoes],
            'resumo': {
                'total_entradas': float(total_entradas),
                'total_saidas': float(total_saidas),
                'saldo': float(saldo)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@financeiro_bp.route('/movimentacoes', methods=['POST'])
@jwt_required()
def create_movimentacao():
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo != 'gerente':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        required_fields = ['tipo', 'valor', 'descricao']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        if data['tipo'] not in ['entrada', 'saida']:
            return jsonify({'error': 'Tipo inválido'}), 400
        
        movimentacao = MovimentacaoFinanceira(
            tipo=data['tipo'],
            descricao=data['descricao'],
            valor=data['valor'],
            forma_pagamento=data.get('forma_pagamento'),
            associado_a=data.get('associado_a')
        )
        
        db.session.add(movimentacao)
        db.session.commit()
        
        return jsonify({
            'message': 'Movimentação criada com sucesso',
            'movimentacao': movimentacao.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@financeiro_bp.route('/repasses', methods=['GET'])
@jwt_required()
def get_repasses():
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo == 'gerente':
            repasses = Repasse.query.order_by(Repasse.periodo.desc()).all()
        elif current_user.tipo == 'barbeiro' and current_user.barbeiro:
            repasses = Repasse.query.filter_by(
                barbeiro_id=current_user.barbeiro.id
            ).order_by(Repasse.periodo.desc()).all()
        else:
            return jsonify({'error': 'Acesso negado'}), 403
        
        return jsonify([repasse.to_dict() for repasse in repasses]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@financeiro_bp.route('/repasses/<int:barbeiro_id>', methods=['GET'])
@jwt_required()
def get_repasses_barbeiro(barbeiro_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        # Verificar permissões
        if current_user.tipo != 'gerente':
            if not (current_user.tipo == 'barbeiro' and current_user.barbeiro and current_user.barbeiro.id == barbeiro_id):
                return jsonify({'error': 'Acesso negado'}), 403
        
        barbeiro = Barbeiro.query.get(barbeiro_id)
        if not barbeiro:
            return jsonify({'error': 'Barbeiro não encontrado'}), 404
        
        repasses = Repasse.query.filter_by(barbeiro_id=barbeiro_id).order_by(
            Repasse.periodo.desc()
        ).all()
        
        return jsonify([repasse.to_dict() for repasse in repasses]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@financeiro_bp.route('/repasses', methods=['POST'])
@jwt_required()
def create_repasse():
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo != 'gerente':
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        required_fields = ['barbeiro_id', 'periodo', 'valor']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        barbeiro = Barbeiro.query.get(data['barbeiro_id'])
        if not barbeiro:
            return jsonify({'error': 'Barbeiro não encontrado'}), 404
        
        # Verificar se já existe repasse para o período
        repasse_existente = Repasse.query.filter_by(
            barbeiro_id=data['barbeiro_id'],
            periodo=data['periodo']
        ).first()
        
        if repasse_existente:
            return jsonify({'error': 'Repasse já existe para este período'}), 409
        
        repasse = Repasse(
            barbeiro_id=data['barbeiro_id'],
            periodo=data['periodo'],
            valor=data['valor'],
            observacoes=data.get('observacoes')
        )
        
        db.session.add(repasse)
        db.session.commit()
        
        return jsonify({
            'message': 'Repasse criado com sucesso',
            'repasse': repasse.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@financeiro_bp.route('/repasses/<int:repasse_id>', methods=['PATCH'])
@jwt_required()
def update_repasse(repasse_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo != 'gerente':
            return jsonify({'error': 'Acesso negado'}), 403
        
        repasse = Repasse.query.get(repasse_id)
        if not repasse:
            return jsonify({'error': 'Repasse não encontrado'}), 404
        
        data = request.get_json()
        
        if 'status' in data:
            if data['status'] not in ['pago', 'nao_pago']:
                return jsonify({'error': 'Status inválido'}), 400
            repasse.status = data['status']
        
        if 'valor' in data:
            repasse.valor = data['valor']
        
        if 'observacoes' in data:
            repasse.observacoes = data['observacoes']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Repasse atualizado com sucesso',
            'repasse': repasse.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@financeiro_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    try:
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)
        
        if current_user.tipo != 'gerente':
            return jsonify({'error': 'Acesso negado'}), 403
        
        hoje = date.today()
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        # Receita do mês atual
        receita_mes = db.session.query(func.sum(MovimentacaoFinanceira.valor)).filter(
            MovimentacaoFinanceira.tipo == 'entrada',
            extract('month', MovimentacaoFinanceira.data) == mes_atual,
            extract('year', MovimentacaoFinanceira.data) == ano_atual
        ).scalar() or 0
        
        # Gastos do mês atual
        gastos_mes = db.session.query(func.sum(MovimentacaoFinanceira.valor)).filter(
            MovimentacaoFinanceira.tipo == 'saida',
            extract('month', MovimentacaoFinanceira.data) == mes_atual,
            extract('year', MovimentacaoFinanceira.data) == ano_atual
        ).scalar() or 0
        
        # Receita do dia
        receita_hoje = db.session.query(func.sum(MovimentacaoFinanceira.valor)).filter(
            MovimentacaoFinanceira.tipo == 'entrada',
            func.date(MovimentacaoFinanceira.data) == hoje
        ).scalar() or 0
        
        # Total de agendamentos por status
        total_agendamentos = db.session.query(Agendamento.status, func.count(Agendamento.id)).group_by(Agendamento.status).all()
        agendamentos_por_status = {status: count for status, count in total_agendamentos}

        # Total de clientes
        total_clientes = Usuario.query.filter_by(tipo=\'cliente\').count()

        # Total de barbeiros
        total_barbeiros = Usuario.query.filter_by(tipo=\'barbeiro\').count()

        return jsonify({
            \'receita_mes\': float(receita_mes),
            \'gastos_mes\': float(gastos_mes),
            \'lucro_mes\': float(receita_mes - gastos_mes),
            \'receita_hoje\': float(receita_hoje),
            \'agendamentos_por_status\': agendamentos_por_status,
            \'total_clientes\': total_clientes,
            \'total_barbeiros\': total_barbeiros
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

