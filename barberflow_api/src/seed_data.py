#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de teste
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, Usuario, Barbeiro, Servico, Produto, barbeiro_servico
from src.main import app
from datetime import datetime

def seed_database():
    with app.app_context():
        # Limpar dados existentes
        db.drop_all()
        db.create_all()
        
        print("Criando usuários...")
        
        # Criar usuário gerente
        gerente = Usuario(
            nome="João Silva",
            email="gerente@barberflow.com",
            senha="123456",
            tipo="gerente",
            telefone="(11) 99999-9999"
        )
        db.session.add(gerente)
        
        # Criar usuários barbeiros
        barbeiro1_user = Usuario(
            nome="Carlos Santos",
            email="carlos@barberflow.com",
            senha="123456",
            tipo="barbeiro",
            telefone="(11) 88888-8888"
        )
        db.session.add(barbeiro1_user)
        
        barbeiro2_user = Usuario(
            nome="Pedro Oliveira",
            email="pedro@barberflow.com",
            senha="123456",
            tipo="barbeiro",
            telefone="(11) 77777-7777"
        )
        db.session.add(barbeiro2_user)
        
        # Criar usuários clientes
        cliente1 = Usuario(
            nome="Maria Fernanda",
            email="maria@email.com",
            senha="123456",
            tipo="cliente",
            telefone="(11) 66666-6666"
        )
        db.session.add(cliente1)
        
        cliente2 = Usuario(
            nome="José Roberto",
            email="jose@email.com",
            senha="123456",
            tipo="cliente",
            telefone="(11) 55555-5555"
        )
        db.session.add(cliente2)
        
        db.session.commit()
        
        print("Criando barbeiros...")
        
        # Criar perfis de barbeiros
        barbeiro1 = Barbeiro(
            usuario_id=barbeiro1_user.id,
            especialidades="Corte masculino, Barba, Bigode",
            horario_de_trabalho={
                "segunda": "09:00-18:00",
                "terca": "09:00-18:00",
                "quarta": "09:00-18:00",
                "quinta": "09:00-18:00",
                "sexta": "09:00-18:00",
                "sabado": "08:00-16:00"
            },
            dias_de_folga="2025-12-25,2026-01-01"
        )
        db.session.add(barbeiro1)
        
        barbeiro2 = Barbeiro(
            usuario_id=barbeiro2_user.id,
            especialidades="Corte feminino, Corte masculino, Escova",
            horario_de_trabalho={
                "segunda": "10:00-19:00",
                "terca": "10:00-19:00",
                "quarta": "10:00-19:00",
                "quinta": "10:00-19:00",
                "sexta": "10:00-19:00",
                "sabado": "09:00-17:00"
            },
            dias_de_folga="2025-12-25,2026-01-01"
        )
        db.session.add(barbeiro2)
        
        db.session.commit()
        
        print("Criando serviços...")
        
        # Criar serviços
        servicos = [
            Servico(nome="Corte Masculino", descricao="Corte de cabelo masculino tradicional", preco=25.00, duracao=30),
            Servico(nome="Corte + Barba", descricao="Corte de cabelo + barba completa", preco=35.00, duracao=45),
            Servico(nome="Apenas Barba", descricao="Aparar e modelar barba", preco=15.00, duracao=20),
            Servico(nome="Corte Feminino", descricao="Corte de cabelo feminino", preco=40.00, duracao=60),
            Servico(nome="Escova", descricao="Escova modeladora", preco=20.00, duracao=30),
        ]
        
        for servico in servicos:
            db.session.add(servico)
        
        db.session.commit()
        
        print("Associando barbeiros aos serviços...")
        
        # Associar barbeiros aos serviços
        # Barbeiro 1 (Carlos) - especialista em cortes masculinos
        barbeiro1.servicos.extend([servicos[0], servicos[1], servicos[2]])  # Corte masculino, Corte + Barba, Apenas Barba
        
        # Barbeiro 2 (Pedro) - faz de tudo
        barbeiro2.servicos.extend(servicos)  # Todos os serviços
        
        db.session.commit()
        
        print("Criando produtos...")
        
        # Criar produtos
        produtos = [
            Produto(nome="Shampoo Anticaspa", tipo="venda", quantidade=50, unidade="unidade", custo_unitario=8.00, preco_venda=15.00),
            Produto(nome="Pomada Modeladora", tipo="venda", quantidade=30, unidade="unidade", custo_unitario=12.00, preco_venda=25.00),
            Produto(nome="Óleo para Barba", tipo="venda", quantidade=20, unidade="unidade", custo_unitario=15.00, preco_venda=30.00),
            Produto(nome="Shampoo Profissional", tipo="uso_interno", quantidade=10, unidade="litro", custo_unitario=25.00, preco_venda=None),
            Produto(nome="Cera Modeladora", tipo="uso_interno", quantidade=5, unidade="unidade", custo_unitario=20.00, preco_venda=None),
        ]
        
        for produto in produtos:
            db.session.add(produto)
        
        db.session.commit()
        
        print("Dados de teste criados com sucesso!")
        print("\nCredenciais de acesso:")
        print("Gerente: gerente@barberflow.com / 123456")
        print("Barbeiro 1: carlos@barberflow.com / 123456")
        print("Barbeiro 2: pedro@barberflow.com / 123456")
        print("Cliente 1: maria@email.com / 123456")
        print("Cliente 2: jose@email.com / 123456")

if __name__ == "__main__":
    seed_database()

