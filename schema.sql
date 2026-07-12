CREATE TABLE IF NOT EXISTS investimentos_iniciais (
    id SERIAL PRIMARY KEY,
    valor_terreno NUMERIC(12,2) NOT NULL,
    custo_edificacao NUMERIC(12,2) NOT NULL,
    impostos_transferencia NUMERIC(12,2) NOT NULL,
    data_aquisicao DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS maquinas (
    id SERIAL PRIMARY KEY,
    nome_maquina VARCHAR(100) NOT NULL,
    preco_compra NUMERIC(12,2) NOT NULL,
    tempo_vida_util_anos INT NOT NULL,
    valor_revenda_estimado NUMERIC(12,2) NOT NULL,
    custo_manutencao_anual NUMERIC(12,2) NOT NULL,
    minutos_ativos_ano INT NOT NULL,
    potencia_kw NUMERIC(8,2) DEFAULT 0.00,
    tarifa_kwh NUMERIC(6,4) DEFAULT 0.0000,
    data_aquisicao DATE NOT NULL,
    data_manutencao_preventiva DATE NOT NULL,
    diametro_trabalho_mm NUMERIC(8,2) DEFAULT 0.00,
    comprimento_trabalho_mm NUMERIC(8,2) DEFAULT 0.00,
    custo_minuto_maquina NUMERIC(10,4) NOT NULL
);

CREATE TABLE IF NOT EXISTS materiais (
    id SERIAL PRIMARY KEY,
    nome_material VARCHAR(150) NOT NULL,
    tipo_material VARCHAR(50) NOT NULL,
    custo_unitario NUMERIC(10,2) NOT NULL,
    unidade_medida VARCHAR(20) DEFAULT 'un'
);

CREATE TABLE IF NOT EXISTS processos (
    id SERIAL PRIMARY KEY,
    codigo_produto VARCHAR(50) UNIQUE NOT NULL,
    nome_produto VARCHAR(150) NOT NULL,
    maquina_id INT REFERENCES maquinas(id) ON DELETE CASCADE,
    tempo_cycle_min NUMERIC(8,2) NOT NULL,
    tempo_setup_min NUMERIC(8,2) NOT NULL,
    lote_padrao INT DEFAULT 100
);

CREATE TABLE IF NOT EXISTS pedidos_venda (
    id SERIAL PRIMARY KEY,
    processo_id INT REFERENCES processos(id) ON DELETE CASCADE,
    quantidade_pedida INT NOT NULL,
    cliente_nome VARCHAR(150) NOT NULL,
    carga_minutos_pcp NUMERIC(10,2) NOT NULL,
    data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
