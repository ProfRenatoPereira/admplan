import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# CONEXAO PERMANENTE COM O BANCO DE DADOS POSTGRESQL DO RENDER
def obter_conexao_db():
    url_banco = os.environ.get('DATABASE_URL')
    if url_banco:
        if url_banco.startswith("postgres://"):
            url_banco = url_banco.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url_banco)
    return None

def inicializar_banco():
    conn = obter_conexao_db()
    if conn:
        try:
            cursor = conn.cursor()
            
            # 1. Tabela Isolada Imobiliária
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS imobiliario_isolado (
                    id SERIAL PRIMARY KEY,
                    descricao VARCHAR(150) NOT NULL,
                    valor_capital NUMERIC(12,2) NOT NULL,
                    valor_aluguel_mercado NUMERIC(12,2) NOT NULL,
                    indice_correcao NUMERIC(5,2) NOT NULL,
                    minutos_operacionais INT NOT NULL,
                    custo_minuto_instalacao NUMERIC(10,4) NOT NULL,
                    meses_retorno NUMERIC(8,1) NOT NULL
                );
            """)
            
            # 2. Tabela Isolada de Ativos e Máquinas Reais
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maquinas_isoladas (
                    id SERIAL PRIMARY KEY,
                    nome_equipamento VARCHAR(150) NOT NULL,
                    tipo_maquina VARCHAR(100) NOT NULL,
                    codigo_identificacao VARCHAR(50) NOT NULL,
                    preco_compra NUMERIC(12,2) NOT NULL,
                    velocidade_trabalho VARCHAR(50) NOT NULL,
                    avanco_trabalho VARCHAR(50) NOT NULL,
                    capacidade_fisica VARCHAR(100) NOT NULL,
                    link_mercado TEXT,
                    minutos_ativos_ano INT NOT NULL DEFAULT 144000
                );
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e: print(f"Erro na sincronizacao: {e}")

inicializar_banco()

# ROTAS DIRETAS DE NAVEGAÇÃO MULTIPÁGINAS
@app.route('/')
def index(): return render_template('index.html')

@app.route('/terreno')
def pagina_terreno(): return render_template('terreno.html')

@app.route('/maquinas')
def pagina_maquinas(): return render_template('maquinas.html')

@app.route('/produtos')
def pagina_produtos(): return render_template('produtos.html')

@app.route('/materiais')
def pagina_materiais(): return render_template('materiais.html')

@app.route('/processos')
def pagina_processos(): return render_template('processos.html')

@app.route('/vendas')
def pagina_vendas(): return render_template('vendas.html')

@app.route('/retorno')
def pagina_retorno(): return render_template('retorno.html')

@app.route('/precificacao')
def pagina_precificacao(): return render_template('precificacao.html')
# API ISOLADA: GESTÃO DE INSTALAÇÕES IMOBILIÁRIAS (AULA 1)
@app.route('/api/imobiliario_isolado', methods=['GET', 'POST', 'PUT'])
@app.route('/api/imobiliario_isolado/<int:item_id>', methods=['DELETE'])
def gerenciar_imobiliario_isolado(item_id=None):
    conn = obter_conexao_db()
    if not conn: return jsonify([])
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'DELETE' and item_id:
        try:
            cursor.execute("DELETE FROM imobiliario_isolado WHERE id = %s;", (item_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500
            
    if request.method in ['POST', 'PUT']:
        data = request.get_json()
        idx = data.get('id')
        desc = data.get('descricao', 'Galpão Industrial')
        capital = float(data.get('valor_capital', 0))
        aluguel = float(data.get('valor_aluguel_mercado', 0))
        indice = float(data.get('indice_correcao', 1.0))
        minutos = int(data.get('minutos_operacionais_ano', 144000))
        
        # Retorno baseado em 50% do aluguel simulado de mercado corrigido por índice
        retorno_mensal_real = (aluguel * 0.5) * (1 + (indice / 100))
        meses_retorno = capital / retorno_mensal_real if retorno_mensal_real > 0 else 0
        custo_minuto = (capital / 240) / minutos if minutos > 0 else 0
        
        try:
            if request.method == 'PUT' and idx:
                cursor.execute(
                    """UPDATE imobiliario_isolado SET descricao=%s, valor_capital=%s, valor_aluguel_mercado=%s, 
                                                     indice_correcao=%s, minutos_operacionais=%s, custo_minuto_instalacao=%s, meses_retorno=%s 
                       WHERE id=%s;""", (desc, capital, aluguel, indice, minutos, custo_minuto, meses_retorno, idx)
                )
            else:
                cursor.execute(
                    """INSERT INTO imobiliario_isolado (descricao, valor_capital, valor_aluguel_mercado, indice_correcao, minutos_operacionais, custo_minuto_instalacao, meses_retorno) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s);""", (desc, capital, aluguel, indice, minutos, custo_minuto, meses_retorno)
                )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500

    cursor.execute("SELECT * FROM imobiliario_isolado ORDER BY id DESC;")
    registros = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(registros)
# API ISOLADA: GESTÃO DE ATIVOS E MÁQUINAS REAIS (AULA 2)
@app.route('/api/maquinas_isoladas', methods=['GET', 'POST', 'PUT'])
@app.route('/api/maquinas_isoladas/<int:maquina_id>', methods=['DELETE'])
def gerenciar_maquinas_isoladas(maquina_id=None):
    conn = obter_conexao_db()
    if not conn: return jsonify([])
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'DELETE' and maquina_id:
        try:
            cursor.execute("DELETE FROM maquinas_isoladas WHERE id = %s;", (maquina_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500
            
    if request.method in ['POST', 'PUT']:
        data = request.get_json()
        idx = data.get('id')
        nome = data.get('nome_equipamento')
        tipo = data.get('tipo_maquina')
        codigo = data.get('codigo_identificacao')
        preco = float(data.get('preco_compra', 0))
        vel = data.get('velocidade_trabalho', 'N/A')
        avanco = data.get('avanco_trabalho', 'N/A')
        cap = data.get('capacidade_fisica', 'N/A')
        link = data.get('link_mercado', '')
        minutos = int(data.get('minutos_ativos_ano', 144000))
        
        try:
            if request.method == 'PUT' and idx:
                cursor.execute(
                    """UPDATE maquinas_isoladas SET nome_equipamento=%s, tipo_machine=%s, codigo_identificacao=%s, 
                                                   preco_compra=%s, velocidade_trabalho=%s, avanco_trabalho=%s, 
                                                   capacidade_fisica=%s, link_mercado=%s, minutos_ativos_ano=%s 
                       WHERE id=%s;""", (nome, tipo, codigo, preco, vel, avanco, cap, link, minutos, idx)
                )
            else:
                cursor.execute(
                    """INSERT INTO maquinas_isoladas (nome_equipamento, tipo_maquina, codigo_identificacao, preco_compra, velocidade_trabalho, avanco_trabalho, capacidade_fisica, link_mercado, minutos_ativos_ano) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);""", (nome, tipo, codigo, preco, vel, avanco, cap, link, minutos)
                )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500

    cursor.execute("SELECT * FROM maquinas_isoladas ORDER BY id DESC;")
    maquinas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(maquinas)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
