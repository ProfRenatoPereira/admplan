CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_number TEXT UNIQUE NOT NULL,
    descricao TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS processos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    nome_operacao TEXT NOT NULL,
    tempo_segundos INTEGER NOT NULL,
    custo_mod REAL NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS materiais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    nome_material TEXT NOT NULL,
    preco_unitario REAL NOT NULL,
    fonte_url TEXT,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS precificacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER UNIQUE NOT NULL,
    margem_lucro REAL NOT NULL,
    impostos REAL NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL,
    quantidade_meta INTEGER NOT NULL,
    FOREIGN KEY (produto_id) REFERENCES produtos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS terrenos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao_imovel TEXT NOT NULL,
    valor_aquisicao REAL NOT NULL,
    impostos_anuais REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS maquinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_maquina TEXT NOT NULL,
    valor_compra REAL NOT NULL,
    depreciacao_anual REAL NOT NULL
);
