from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # cliente, barbeiro, gerente
    foto = db.Column(db.String(255))
    telefone = db.Column(db.String(20))
    
    # Relacionamentos
    barbeiro = db.relationship('Barbeiro', backref='usuario', uselist=False, cascade='all, delete-orphan')
    agendamentos_cliente = db.relationship('Agendamento', foreign_keys='Agendamento.cliente_id', backref='cliente')
    vendas = db.relationship('VendaProduto', backref='cliente')

    def __init__(self, nome, email, senha, tipo, foto=None, telefone=None):
        self.nome = nome
        self.email = email
        self.senha = generate_password_hash(senha)
        self.tipo = tipo
        self.foto = foto
        self.telefone = telefone

    def verificar_senha(self, senha):
        return check_password_hash(self.senha, senha)

    def __repr__(self):
        return f'<Usuario {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'tipo': self.tipo,
            'foto': self.foto,
            'telefone': self.telefone
        }

class Barbeiro(db.Model):
    __tablename__ = 'barbeiros'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    especialidades = db.Column(db.Text)
    horario_de_trabalho = db.Column(db.JSON)
    dias_de_folga = db.Column(db.Text)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='barbeiro')
    repasses = db.relationship('Repasse', backref='barbeiro')
    servicos = db.relationship('Servico', secondary='barbeiro_servico', backref='barbeiros')

    def __repr__(self):
        return f'<Barbeiro {self.usuario.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'nome': self.usuario.nome,
            'especialidades': self.especialidades,
            'horario_de_trabalho': self.horario_de_trabalho,
            'dias_de_folga': self.dias_de_folga
        }

class Servico(db.Model):
    __tablename__ = 'servicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    duracao = db.Column(db.Integer, nullable=False)  # em minutos
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='servico')

    def __repr__(self):
        return f'<Servico {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco': float(self.preco),
            'duracao': self.duracao
        }

# Tabela de associação para barbeiros e serviços
barbeiro_servico = db.Table('barbeiro_servico',
    db.Column('barbeiro_id', db.Integer, db.ForeignKey('barbeiros.id'), primary_key=True),
    db.Column('servico_id', db.Integer, db.ForeignKey('servicos.id'), primary_key=True)
)

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pendente')  # pendente, confirmado, realizado, cancelado
    valor_final = db.Column(db.Numeric(10, 2))
    forma_pagamento = db.Column(db.String(100))
    
    __table_args__ = (db.UniqueConstraint('barbeiro_id', 'data', 'hora', name='unique_barbeiro_horario'),)

    def __repr__(self):
        return f'<Agendamento {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'cliente_nome': self.cliente.nome,
            'barbeiro_id': self.barbeiro_id,
            'barbeiro_nome': self.barbeiro.usuario.nome,
            'servico_id': self.servico_id,
            'servico_nome': self.servico.nome,
            'data': self.data.isoformat(),
            'hora': self.hora.strftime('%H:%M'),
            'status': self.status,
            'valor_final': float(self.valor_final) if self.valor_final else None,
            'forma_pagamento': self.forma_pagamento
        }

class Produto(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # venda, uso_interno
    quantidade = db.Column(db.Integer, nullable=False)
    unidade = db.Column(db.String(50))
    custo_unitario = db.Column(db.Numeric(10, 2))
    preco_venda = db.Column(db.Numeric(10, 2))
    
    # Relacionamentos
    vendas = db.relationship('VendaProduto', backref='produto')

    def __repr__(self):
        return f'<Produto {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'quantidade': self.quantidade,
            'unidade': self.unidade,
            'custo_unitario': float(self.custo_unitario) if self.custo_unitario else None,
            'preco_venda': float(self.preco_venda) if self.preco_venda else None
        }

class VendaProduto(db.Model):
    __tablename__ = 'vendas_produto'
    
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    quantidade = db.Column(db.Integer, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<VendaProduto {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'produto_id': self.produto_id,
            'produto_nome': self.produto.nome,
            'cliente_id': self.cliente_id,
            'cliente_nome': self.cliente.nome if self.cliente else None,
            'quantidade': self.quantidade,
            'valor_total': float(self.valor_total),
            'data': self.data.isoformat()
        }

class MovimentacaoFinanceira(db.Model):
    __tablename__ = 'movimentacoes_financeiras'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # entrada, saida
    descricao = db.Column(db.Text)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    forma_pagamento = db.Column(db.String(100))
    associado_a = db.Column(db.String(100))  # venda, servico, repasse, compra_insumo

    def __repr__(self):
        return f'<MovimentacaoFinanceira {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'valor': float(self.valor),
            'data': self.data.isoformat(),
            'forma_pagamento': self.forma_pagamento,
            'associado_a': self.associado_a
        }

class Repasse(db.Model):
    __tablename__ = 'repasses'
    
    id = db.Column(db.Integer, primary_key=True)
    barbeiro_id = db.Column(db.Integer, db.ForeignKey('barbeiros.id'), nullable=False)
    periodo = db.Column(db.String(50), nullable=False)  # YYYY-MM
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='nao_pago')  # pago, nao_pago
    observacoes = db.Column(db.Text)

    def __repr__(self):
        return f'<Repasse {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'barbeiro_id': self.barbeiro_id,
            'barbeiro_nome': self.barbeiro.usuario.nome,
            'periodo': self.periodo,
            'valor': float(self.valor),
            'status': self.status,
            'observacoes': self.observacoes
        }
