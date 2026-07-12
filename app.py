import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, jsonify, request, render_template_string

app = Flask(__name__)

# CONEXAO ESTAVEL COM O BANCO DE DADOS POSTGRESQL DO RENDER
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
            if os.path.exists('schema.sql'):
                with open('schema.sql', 'r', encoding='utf-8') as f:
                    cursor.execute(f.read())
                conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Erro na sincronizacao: {e}")

inicializar_banco()

# ROTAS FISICAS DAS SUAS AULAS INDEPENDENTES
@app.route('/')
def index(): return render_template('index.html')

@app.route('/terreno')
def pagina_terreno(): return render_template('terreno.html')

@app.route('/maquinas')
def pagina_maquinas(): return render_template('maquinas.html')

@app.route('/materiais')
def pagina_materiais(): return render_template('materiais.html')

@app.route('/processos')
def pagina_processos(): return render_template('processos.html')

@app.route('/precificacao')
def pagina_precificacao(): return render_template('precificacao.html')

@app.route('/vendas')
def pagina_vendas(): return render_template('vendas.html')
# API: CONTROLE DO VALOR DO IMOVEL DA PLANTA INDUSTRIAL
@app.route('/api/imobiliario', methods=['GET', 'POST'])
def gerenciar_imobiliario():
    conn = obter_conexao_db()
    if not conn: return jsonify({'error': 'Sem conexao'}), 500
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        data = request.get_json()
        v_terr = float(data.get('valor_terreno', 0))
        c_edif = float(data.get('custo_edificacao', 0))
        imp = float(data.get('impostos_anuais', 0))
        v_util = int(data.get('vida_util_anos', 20))
        h_ano = int(data.get('horas_operacionais_ano', 2400))
        
        amort = (v_terr + c_edif) / v_util
        c_anual = amort + imp
        min_ano = h_ano * 60
        c_min = c_anual / min_ano if min_ano > 0 else 0
        
        try:
            cursor.execute("DELETE FROM investimentos_iniciais;")
            cursor.execute(
                "INSERT INTO investimentos_iniciais (valor_terreno, custo_edificacao, impostos_transferencia) VALUES (%s, %s, %s);", 
                (v_terr, c_edif, imp)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso', 'custoMinutoInstalacao': round(c_min, 4)})
        except Exception as e: return jsonify({'error': str(e)}), 500
            
    cursor.execute("SELECT * FROM investimentos_iniciais ORDER BY id DESC LIMIT 1;")
    imovel = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(imovel or {})

# API: CRUD DE MAQUINAS COM EFICIENCIA ENERGETICA Y PARAMETROS METALURGICOS
@app.route('/api/maquinas', methods=['GET', 'POST', 'PUT'])
@app.route('/api/maquinas/<int:maquina_id>', methods=['DELETE'])
def gerenciar_maquinas(maquina_id=None):
    conn = obter_conexao_db()
    if not conn: return jsonify([])
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'DELETE' and maquina_id:
        try:
            cursor.execute("DELETE FROM maquinas WHERE id = %s;", (maquina_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500
            
    if request.method in ['POST', 'PUT']:
        data = request.get_json()
        id_m = data.get('id')
        nome = data.get('nome')
        preco = float(data.get('preco', 0))
        v_ut = int(data.get('vida_util', 1))
        v_rev = float(data.get('valor_revenda', 0))
        manut = float(data.get('manutencao', 0))
        h_an = int(data.get('horas_ano', 1))
        pot = float(data.get('potencia_kw', 0))
        tar = float(data.get('tarifa_kwh', 0))
        dt_aq = data.get('data_aquisicao') or '2026-01-15'
        dt_mn = data.get('data_manutencao') or '2026-12-20'
        diam = float(data.get('diametro_mm', 0))
        comp = float(data.get('comprimento_mm', 0))
        
        depr = (preco - v_rev) / v_ut if preco > v_rev else 0
        min_ano = h_an * 60
        c_energ = (pot * tar) / 60.0
        c_min = ((depr + manut) / min_ano) + c_energ
        try:
            if request.method == 'PUT' and id_m:
                cursor.execute(
                    """UPDATE maquinas SET nome_maquina=%s, preco_compra=%s, tempo_vida_util_anos=%s, valor_revenda_estimado=%s, 
                                          custo_manutencao_anual=%s, horas_ativas_ano=%s, potencia_kw=%s, tarifa_kwh=%s, 
                                          data_aquisicao=%s, data_manutencao_preventiva=%s, diametro_trabalho_mm=%s, comprimento_trabalho_mm=%s, custo_minuto_maquina=%s 
                       WHERE id=%s;""", (nome, preco, v_ut, v_rev, manut, h_an, pot, tar, dt_aq, dt_mn, diam, comp, c_min, id_m)
                )
            else:
                cursor.execute(
                    """INSERT INTO maquinas (nome_maquina, preco_compra, tempo_vida_util_anos, valor_revenda_estimado, custo_manutencao_anual, 
                                            horas_ativas_ano, potencia_kw, tarifa_kwh, data_aquisicao, data_manutencao_preventiva, 
                                            diametro_trabalho_mm, comprimento_trabalho_mm, custo_minuto_maquina) 
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""", (nome, preco, v_ut, v_rev, manut, h_an, pot, tar, dt_aq, dt_mn, diam, comp, c_min)
                )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500

    cursor.execute("SELECT * FROM maquinas ORDER BY id DESC;")
    maquinas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(maquinas)

# API: CRUD DE ENGENHARIA DE MATERIAIS, FERRAMENTAS E MATERIA-PRIMA
@app.route('/api/materiais', methods=['GET', 'POST', 'PUT'])
@app.route('/api/materiais/<int:material_id>', methods=['DELETE'])
def gerenciar_materiais(material_id=None):
    conn = obter_conexao_db()
    if not conn: return jsonify([])
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'DELETE' and material_id:
        try:
            cursor.execute("DELETE FROM materiais WHERE id = %s;", (material_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500
            
    if request.method in ['POST', 'PUT']:
        data = request.get_json()
        id_mat = data.get('id')
        nome = data.get('nome')
        tipo = data.get('tipo')
        custo_un = float(data.get('custo_unitario', 0))
        unidade = data.get('unidade_medida', 'un')
        
        try:
            if request.method == 'PUT' and id_mat:
                cursor.execute("UPDATE materiais SET nome_material=%s, tipo_material=%s, custo_unitario=%s, unidade_medida=%s WHERE id=%s;", (nome, tipo, custo_un, unidade, id_mat))
            else:
                cursor.execute("INSERT INTO materiais (nome_material, tipo_material, custo_unitario, unidade_medida) VALUES (%s, %s, %s, %s);", (nome, tipo, custo_un, unidade))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500

    cursor.execute("SELECT * FROM materiais ORDER BY nome_material ASC;")
    materiais = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(materiais)
# API: CADASTRO DE PRODUTOS, ROTEIROS DE ETAPAS E PCP INDUSTRIAL
@app.route('/api/processos', methods=['GET', 'POST', 'PUT'])
@app.route('/api/processos/<int:processo_id>', methods=['DELETE'])
def gerenciar_processos(processo_id=None):
    conn = obter_conexao_db()
    if not conn: return jsonify([])
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'DELETE' and processo_id:
        try:
            cursor.execute("DELETE FROM processos WHERE id = %s;", (processo_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500
            
    if request.method in ['POST', 'PUT']:
        data = request.get_json()
        id_proc = data.get('id')
        cod_prod = data.get('codigo_produto')
        nome_prod = data.get('nome_produto')
        maq_id = int(data.get('maquina_id'))
        t_ciclo = float(data.get('tempo_ciclo_min', 0))
        t_setup = float(data.get('tempo_setup_min', 0))
        lote = int(data.get('lote_padrao', 100))
        
        try:
            if request.method == 'PUT' and id_proc:
                cursor.execute("UPDATE processos SET codigo_produto=%s, nome_produto=%s, maquina_id=%s, tempo_ciclo_min=%s, tempo_setup_min=%s, lote_padrao=%s WHERE id=%s;", (cod_prod, nome_prod, maq_id, t_ciclo, t_setup, lote, id_proc))
            else:
                cursor.execute("INSERT INTO processos (codigo_produto, nome_produto, maquina_id, tempo_ciclo_min, tempo_setup_min, lote_padrao) VALUES (%s, %s, %s, %s, %s, %s);", (cod_prod, nome_prod, maq_id, t_ciclo, t_setup, lote))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500

    cursor.execute("SELECT p.*, m.nome_maquina, m.custo_minuto_maquina FROM processos p LEFT JOIN maquinas m ON p.maquina_id = m.id ORDER BY p.codigo_produto ASC;")
    processos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(processos)

# API: EMISSAO E PLANEJAMENTO DE PEDIDOS DE VENDAS E PRODUÇÃO (PCP)
@app.route('/api/vendas', methods=['GET', 'POST'])
@app.route('/api/vendas/<int:pedido_id>', methods=['DELETE'])
def gerenciar_vendas(pedido_id=None):
    conn = obter_conexao_db()
    if not conn: return jsonify([])
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'DELETE' and pedido_id:
        try:
            cursor.execute("DELETE FROM pedidos_venda WHERE id = %s;", (pedido_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500
            
    if request.method == 'POST':
        data = request.get_json()
        processo_id = int(data.get('processo_id'))
        qtd_pedida = int(data.get('quantidade', 0))
        cliente = data.get('cliente', 'Cliente Geral')
        
        cursor.execute("SELECT tempo_ciclo_min, tempo_setup_min FROM processos WHERE id = %s;", (processo_id,))
        prod = cursor.fetchone()
        tempo_total_producao_min = 0
        if prod: tempo_total_producao_min = (qtd_pedida * float(prod['tempo_ciclo_min'])) + float(prod['tempo_setup_min'])
            
        try:
            cursor.execute("INSERT INTO pedidos_venda (processo_id, quantidade_pedida, cliente_nome, carga_horas_pcp) VALUES (%s, %s, %s, %s);", (processo_id, qtd_pedida, cliente, round(tempo_total_producao_min / 60.0, 2)))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'sucesso'})
        except Exception as e: return jsonify({'error': str(e)}), 500

    cursor.execute("SELECT v.*, p.codigo_produto, p.nome_produto FROM pedidos_venda v LEFT JOIN processos p ON v.processo_id = p.id ORDER BY v.id DESC;")
    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(pedidos)

# API: SIMULADOR DE MARK-UP
@app.route('/api/calculo-markup', methods=['POST'])
def calcular_markup():
    data = request.get_json()
    c_tot = float(data.get('custo_total', 0))
    luc = float(data.get('margem_lucro', 0))
    imp = float(data.get('impostos', 0))
    den = 1 - ((luc + imp) / 100)
    if den <= 0: return jsonify({'error': 'Erro'}), 400
    return jsonify({'markup': round(1/den, 2), 'preco_venda': round(c_tot * (1/den), 2)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
