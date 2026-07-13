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
            # Criação da tabela imobiliária flexível e isolada
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
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e: print(f"Erro banco: {e}")

inicializar_banco()

# ROTAS DIRETAS DAS PÁGINAS DE TRABALHO
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
# API ISOLADA: GERENCIAMENTO DE INSTALAÇÕES IMOBILIÁRIAS (AULA 1)
@app.route('/api/imobiliario_isolado', methods=['GET', 'POST', 'PUT'])
@app.route('/api/imobiliario_isolado/<int:item_id>', methods=['DELETE'])
def gerenciar_imobiliario_isolado(item_id=None):
    conn = obter_conexao_db()
    if not conn: return jsonify([])
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # 1. BOTÃO DELETAR (Remoção física permanente do PostgreSQL)
    if request.method == 'DELETE' and item_id:
        try:
            cursor.execute("DELETE FROM imobiliario_isolado WHERE id = %s;", (item_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500
            
    # 2. BOTÕES SALVAR E ALTERAR
    if request.method in ['POST', 'PUT']:
        data = request.get_json()
        idx = data.get('id')
        desc = data.get('descricao', 'Galpão Industrial')
        capital = float(data.get('valor_capital', 0))
        aluguel = float(data.get('valor_aluguel_mercado', 0))
        indice = float(data.get('indice_correcao', 1.0))
        minutos = int(data.get('minutos_operacionais_ano', 144000))
        
        # NOVA LÓGICA PEDAGÓGICA FLEXÍVEL: Retorno baseado em 50% do aluguel corrigido
        retorno_mensal_real = (aluguel * 0.5) * (1 + (indice / 100))
        meses_retorno = capital / retorno_mensal_real if retorno_mensal_real > 0 else 0
        
        # Custo minuto de instalação padrão para tabelas internas
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

    # 3. LEITURA PERMANENTE DAS TABELAS ABAIXO DO CADASTRO
    cursor.execute("SELECT * FROM imobiliario_isolado ORDER BY id DESC;")
    registros = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(registros)
# FIM DO ARQUIVO COMPILÁVEL DO FLASK NO RENDER
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
