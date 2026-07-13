import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for
from whitenoise import WhiteNoise

app = Flask(__name__)

# ATIVAÇÃO DO WHITENOISE: Serve os arquivos de estilo CSS e JS direto no Render
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# CRIAÇÃO DO BANCO AUTOMÁTICA: Roda na primeira requisição recebida pelo servidor
@app.before_request
def init_db_on_start():
    if not os.path.exists(DATABASE):
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# ROTA: PRODUTOS (PÁGINA INICIAL / CADASTRO MESTRE)
@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    if request.method == 'POST':
        part_number = request.form.get('part_number')
        descricao = request.form.get('descricao')
        try:
            db.execute("INSERT INTO produtos (part_number, descricao) VALUES (?, ?)", (part_number, descricao))
            db.commit()
        except sqlite3.IntegrityError:
            pass
        return redirect(url_for('index'))
    
    produtos = db.execute("SELECT * FROM produtos").fetchall()
    return render_template('index.html', produtos=produtos)

# ROTA: ENGENHARIA DE PROCESSOS (VINCULADO AO PRODUTO)
@app.route('/processos', methods=['GET', 'POST'])
def procesos():
    db = get_db()
    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        nome_operacao = request.form.get('nome_operacao')
        tempo = request.form.get('tempo')
        custo_mod = request.form.get('custo_mod')
        
        db.execute("INSERT INTO processos (produto_id, nome_operacao, tempo_segundos, custo_mod) VALUES (?, ?, ?, ?)", 
                   (produto_id, nome_operacao, tempo, custo_mod))
        db.commit()
        return redirect(url_for('procesos'))
        
    produtos = db.execute("SELECT * FROM produtos").fetchall()
    processos_salvos = db.execute("""
        SELECT p.*, prod.part_number, prod.descricao FROM processos p 
        JOIN produtos prod ON p.produto_id = prod.id
    """).fetchall()
    return render_template('processos.html', produtos=produtos, processos=processos_salvos)

# ROTA: MATERIAIS & INSUMOS (VINCULADO AO PRODUTO)
@app.route('/materiais', methods=['GET', 'POST'])
def materiais():
    db = get_db()
    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        nome_material = request.form.get('nome_material')
        preco = request.form.get('preco_unitario')
        url = request.form.get('fonte_url')
        
        db.execute("INSERT INTO materiais (produto_id, nome_material, preco_unitario, fonte_url) VALUES (?, ?, ?, ?)", 
                   (produto_id, nome_material, preco, url))
        db.commit()
        return redirect(url_for('materiais'))
        
    produtos = db.execute("SELECT * FROM produtos").fetchall()
    materiais_salvos = db.execute("""
        SELECT m.*, prod.part_number FROM materiais m 
        JOIN produtos prod ON m.produto_id = prod.id
    """).fetchall()
    return render_template('materiais.html', produtos=produtos, materiais=materiais_salvos)
# ROTA: PRECIFICACAO E MARK-UP INDIVIDUAL
@app.route('/precificacao', methods=['GET', 'POST'])
def precificacao():
    db = get_db()
    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        margem_lucro = request.form.get('margem_lucro')
        impostos = request.form.get('impostos')
        
        db.execute("INSERT INTO precificacao (produto_id, margem_lucro, impostos) VALUES (?, ?, ?)", 
                   (produto_id, margem_lucro, impostos))
        db.commit()
        return redirect(url_for('precificacao'))
        
    produtos = db.execute("SELECT * FROM produtos").fetchall()
    dados_precificacao = db.execute("""
        SELECT pr.id, prod.part_number, prod.descricao,
               COALESCE((SELECT SUM(m.preco_unitario) FROM materiais m WHERE m.produto_id = prod.id), 0) as custo_mat,
               COALESCE((SELECT SUM((p.tempo_segundos / 3600.0) * p.custo_mod) FROM processos p WHERE p.produto_id = prod.id), 0) as custo_mod,
               pr.margem_lucro, pr.impostos
        FROM precificacao pr
        JOIN produtos prod ON pr.produto_id = prod.id
    """).fetchall()
    return render_template('precificacao.html', produtos=produtos, precificacoes=dados_precificacao)

# ROTA: ENGENHARIA DE VENDAS
@app.route('/vendas', methods=['GET', 'POST'])
def vendas():
    db = get_db()
    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        quantidade_meta = request.form.get('quantidade_meta')
        
        db.execute("INSERT INTO vendas (produto_id, quantidade_meta) VALUES (?, ?)", 
                   (produto_id, quantidade_meta))
        db.commit()
        return redirect(url_for('vendas'))
        
    produtos = db.execute("SELECT * FROM produtos").fetchall()
    vendas_salvas = db.execute("""
        SELECT v.*, prod.part_number, prod.descricao 
        FROM vendas v 
        JOIN produtos prod ON v.produto_id = prod.id
    """).fetchall()
    return render_template('vendas.html', produtos=produtos, vendas=vendas_salvas)

# ROTA: INVESTIMENTO IMOBILIÁRIO (terreno.html)
@app.route('/terreno', methods=['GET', 'POST'])
def terreno():
    db = get_db()
    if request.method == 'POST':
        descricao = request.form.get('descricao_imovel')
        valor = request.form.get('valor_aquisicao')
        impostos = request.form.get('impostos_anuais')
        
        db.execute("INSERT INTO terrenos (descricao_imovel, valor_aquisicao, impostos_anuais) VALUES (?, ?, ?)", 
                   (descricao, valor, impostos))
        db.commit()
        return redirect(url_for('terreno'))
        
    terrenos_salvos = db.execute("SELECT * FROM terrenos").fetchall()
    return render_template('terreno.html', terrenos=terrenos_salvos)

# ROTA: ATIVOS & MÁQUINAS CNC (maquinas.html)
@app.route('/maquinas', methods=['GET', 'POST'])
def maquinas():
    db = get_db()
    if request.method == 'POST':
        nome = request.form.get('nome_maquina')
        valor = request.form.get('valor_compra')
        depreciacao = request.form.get('depreciacao_anual')
        
        db.execute("INSERT INTO maquinas (nome_maquina, valor_compra, depreciacao_anual) VALUES (?, ?, ?)", 
                   (nome, valor, depreciacao))
        db.commit()
        return redirect(url_for('maquinas'))
        
    maquinas_salvas = db.execute("SELECT * FROM maquinas").fetchall()
    return render_template('maquinas.html', maquinas=maquinas_salvas)

# ROTA: FINANÇAS & RETORNO ACIONISTAS (ROI)
@app.route('/retorno')
def retorno():
    db = get_db()
    indicadores = db.execute("""
        SELECT prod.part_number, prod.descricao, v.quantidade_meta,
               COALESCE((SELECT SUM(m.preco_unitario) FROM materiais m WHERE m.produto_id = prod.id), 0) as mat_total,
               COALESCE((SELECT SUM((p.tempo_segundos / 3600.0) * p.custo_mod) FROM processes p WHERE p.produto_id = prod.id), 0) as mod_total
        FROM produtos prod
        JOIN vendas v ON v.produto_id = prod.id
    """).fetchall()
    # Corrigido aqui: passando 'indicadores' exatamente como o seu retorno.html espera
    return render_template('retorno.html', indicadores=indicadores)

if __name__ == '__main__':
    app.run(debug=True)
