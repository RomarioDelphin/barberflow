CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL, -- Senha criptografada
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN (
        'cliente',
        'barbeiro',
        'gerente'
    )),
    foto VARCHAR(255),
    telefone VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS barbeiros (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    especialidades TEXT,
    horario_de_trabalho JSONB, -- Armazenar como JSON para flexibilidade
    dias_de_folga TEXT -- Ex: 'YYYY-MM-DD,YYYY-MM-DD'
);

CREATE TABLE IF NOT EXISTS servicos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10, 2) NOT NULL,
    duracao INTEGER NOT NULL -- Em minutos
);

CREATE TABLE IF NOT EXISTS barbeiro_servico (
    barbeiro_id INTEGER NOT NULL REFERENCES barbeiros(id) ON DELETE CASCADE,
    servico_id INTEGER NOT NULL REFERENCES servicos(id) ON DELETE CASCADE,
    PRIMARY KEY (barbeiro_id, servico_id)
);

CREATE TABLE IF NOT EXISTS agendamentos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    barbeiro_id INTEGER NOT NULL REFERENCES barbeiros(id) ON DELETE CASCADE,
    servico_id INTEGER NOT NULL REFERENCES servicos(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN (
        'pendente',
        'confirmado',
        'realizado',
        'cancelado'
    )),
    valor_final DECIMAL(10, 2),
    forma_pagamento VARCHAR(100),
    UNIQUE (barbeiro_id, data, hora) -- Garante que um barbeiro não tenha agendamentos duplicados no mesmo horário
);

CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN (
        'venda',
        'uso_interno'
    )),
    quantidade INTEGER NOT NULL,
    unidade VARCHAR(50),
    custo_unitario DECIMAL(10, 2),
    preco_venda DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS vendas_produto (
    id SERIAL PRIMARY KEY,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
    cliente_id INTEGER REFERENCES usuarios(id) ON DELETE
    SET
        NULL, -- Cliente pode ser nulo para vendas no balcão
        quantidade INTEGER NOT NULL,
        valor_total DECIMAL(10, 2) NOT NULL,
        data TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS movimentacoes_financeiras (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN (
        'entrada',
        'saida'
    )),
    descricao TEXT,
    valor DECIMAL(10, 2) NOT NULL,
    data TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    forma_pagamento VARCHAR(100),
    associado_a VARCHAR(100) -- Ex: 'venda', 'servico', 'repasse', 'compra_insumo'
);

CREATE TABLE IF NOT EXISTS repasses (
    id SERIAL PRIMARY KEY,
    barbeiro_id INTEGER NOT NULL REFERENCES barbeiros(id) ON DELETE CASCADE,
    periodo VARCHAR(50) NOT NULL, -- Ex: 'YYYY-MM'
    valor DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN (
        'pago',
        'nao_pago'
    )),
    observacoes TEXT
);


