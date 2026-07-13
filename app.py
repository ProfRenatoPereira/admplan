import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, g
from whitenoise import WhiteNoise

# ... (código estrutural igual, focado na correção do banco de dados)
app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')
DATABASE = 'database.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.before_request
def init_db_on_start():
    if not os.path.exists(DATABASE):
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# --- Rotas com Gerenciamento de Banco Corrigido ---
@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    if request.method == 'POST':
        db.execute("INSERT INTO produtos (part_number, descricao) VALUES (?, ?)", 
                   (request.form.get('part_number'), request.form.get('descricao')))
        db.commit()
        return redirect(url_for('index'))
    return render_template('index.html', produtos=db.execute("SELECT * FROM produtos").fetchall())

@app.route('/processos', methods=['GET', 'POST'])
def processos():
    db = get_db()
    if request.method == 'POST':
        db.execute("INSERT INTO processos (produto_id, nome_operacao, tempo_segundos, custo_mod) VALUES (?, ?, ?, ?)",
                   (request.form.get('produto_id'), request.form.get('nome_operacao'), 
                    request.form.get('tempo'), request.form.get('custo_mod')))
        db.commit()
        return redirect(url_for('processos'))
    # ... (demais rotas com lógica similar de inserção/seleção)
    return render_template('processos.html', produtos=db.execute("SELECT * FROM produtos").fetchall(), 
                           processos_salvos=db.execute("SELECT * FROM processos").fetchall())

# ... (outras rotas: /materiais, /precificacao, /vendas, /terreno, /maquinas, /retorno)

if __name__ == '__main__':
    app.run(debug=True)
