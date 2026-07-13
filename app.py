import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        with app.app_context():
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
            pass # Ignora duplicados ou trate o erro
        return redirect(url_for('index'))
    
    produtos = db.execute("SELECT * FROM produtos").fetchall()
    return render_template('index.html', produtos=produtos)

# ROTA: PROCESSOS (VINCULADO AO PRODUTO)
@app.route('/processos', methods=['GET', 'POST'])
def processos():
    db = get_db()
    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        nome_operacao = request.form.get('nome_operacao')
        tempo = request.form.get('tempo')
        custo_mod = request.form.get('custo_mod')
        
        db.execute("INSERT INTO processos (produto_id, nome_operacao, tempo_segundos, custo_mod) VALUES (?, ?, ?, ?)", 
                   (produto_id, nome_operacao, tempo, custo_mod))
        db.commit()
        return redirect(url_for('processos'))
        
    produtos = db.execute("SELECT * FROM produtos").fetchall()
    processos_salvos = db.execute("""
        SELECT p.*, prod.part_number, prod.descricao FROM processos p 
        JOIN produtos prod ON p.produto_id = prod.id
    """).fetchall()
    return render_template('processos.html', produtos=produtos, processos=processos_salvos)

# ROTA: MATERIAIS (VINCULADO AO PRODUTO + URL DA INTERNET)
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
