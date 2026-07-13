let registrosImobiliarios = [];
let listaMaquinasIsoladas = [];
let listaMateriaisIsolados = [];

document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            const exp = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', !exp);
            navMenu.classList.toggle('active');
        });
    }

    // DISPARADORES FIXOS POR TELA (Trabalham sozinhos sem interferências)
    if (document.getElementById('tabelaImobiliarioIsolado')) carregarImobiliarioIsolado();
    if (document.getElementById('tabelaMaquinasIsoladas')) carregarMaquinasIsoladas();
    if (document.getElementById('tabelaMateriaisIsolados')) carregarMateriaisIsolados();
});

function toggleContraste() { document.body.classList.toggle('alto-contraste'); }
let tamanhoFonteAtual = 100;
function alterarFonte(dir) {
    tamanhoFonteAtual += (dir * 10);
    if (tamanhoFonteAtual >= 80 && tamanhoFonteAtual <= 140) document.documentElement.style.fontSize = `${tamanhoFonteAtual}%`;
}



// ============================================================================
// MÓDULO 1: CÁLCULOS IMOBILIÁRIOS ISOLADOS
// ============================================================================
async function carregarImobiliarioIsolado() {
    const response = await fetch('/api/imobiliario_isolado');
    if (response.ok) { registrosImobiliarios = await response.json(); renderizarTabelaImobiliarioIsolado(); }
}

function renderizarTabelaImobiliarioIsolado() {
    const tbody = document.querySelector('#tabelaImobiliarioIsolado tbody'); if (!tbody) return; tbody.innerHTML = '';
    registrosImobiliarios.forEach(item => {
        const tr = document.createElement('tr');
        const capital = parseFloat(item.valor_capital).toFixed(2);
        const aluguelSimulado = ((parseFloat(item.valor_aluguel_mercado) * 0.5) * (1 + (parseFloat(item.indice_correcao) / 100))).toFixed(2);
        const custoMin = parseFloat(item.custo_minuto_instalacao).toFixed(4);
        const meses = parseFloat(item.meses_retorno).toFixed(1);
        tr.innerHTML = `<td>#${item.id}</td><td><strong>${item.descricao}</strong></td><td>R$ ${capital}</td><td style="color:var(--accent); font-weight:bold;">R$ ${aluguelSimulado}</td><td>R$ ${custoMin}</td><td><strong>${meses} meses</strong></td><td><button onclick="carregarParaAlterar(${item.id})" class="btn-alt">Alterar</button><button onclick="deletarRegistroIsolado(${item.id})" class="btn-del">Deletar</button></td>`;
        tbody.appendChild(tr);
    });
}

async function salvarImobiliarioIsolado() {
    const id = document.getElementById('imoIsoladoId').value; const descricao = document.getElementById('imoDescricao').value.trim();
    const valor_capital = parseFloat(document.getElementById('imoCapital').value) || 0; const valor_aluguel_mercado = parseFloat(document.getElementById('imoAluguel').value) || 0;
    const indice_correcao = parseFloat(document.getElementById('imoIndice').value) || 0; const minutos_operacionais_ano = parseInt(document.getElementById('imoMinutos').value) || 144000;
    if (!descricao || valor_capital <= 0) { alert("Preencha os campos."); return; }
    const response = await fetch('/api/imobiliario_isolado', { method: id ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, descricao, valor_capital, valor_aluguel_mercado, indice_correcao, minutos_operacionais_ano }) });
    if (response.ok) { document.getElementById('imoIsoladoId').value = ''; document.getElementById('imoDescricao').value = ''; document.getElementById('btnSalvarImo').innerText = "Salvar / Registrar Instalação"; carregarImobiliarioIsolado(); }
}

function carregarParaAlterar(id) {
    const item = registrosImobiliarios.find(i => i.id === id); if (!item) return;
    document.getElementById('imoIsoladoId').value = item.id; document.getElementById('imoDescricao').value = item.descricao;
    document.getElementById('imoCapital').value = item.valor_capital; document.getElementById('imoAluguel').value = item.valor_aluguel_mercado;
    document.getElementById('imoIndice').value = item.indice_correcao; document.getElementById('imoMinutos').value = item.minutos_operacionais;
    document.getElementById('btnSalvarImo').innerText = "Salvar Alterações no Banco";
}

async function deletarRegistroIsolado(id) {
    if (!confirm("Deletar imóvel?")) return;
    const response = await fetch(`/api/imobiliario_isolado/${id}`, { method: 'DELETE' }); if (response.ok) carregarImobiliarioIsolado();
}



// ============================================================================
// MÓDULO 2: ATIVOS E MÁQUINAS REAIS DE MERCADO
// ============================================================================
async function carregarMaquinasIsoladas() {
    const r = await fetch('/api/maquinas_isoladas');
    if (r.ok) { listaMaquinasIsoladas = await r.json(); renderizarTabelaMaquinasIsoladas(); }
}

function renderizarTabelaMaquinasIsoladas() {
    const tbody = document.querySelector('#tabelaMaquinasIsoladas tbody'); if (!tbody) return; tbody.innerHTML = '';
    listaMaquinasIsoladas.forEach(m => {
        const tr = document.createElement('tr'); const preco = parseFloat(m.preco_compra).toFixed(2);
        const linkFmt = m.link_mercado ? `<a href="${m.link_mercado}" target="_blank" style="color:#2980b9; font-weight:600; text-decoration:underline;">Ver Oferta 🔗</a>` : 'Pesquisar 🔍';
        tr.innerHTML = `<td><span class="badge-pcp" style="background-color:var(--primary);">${m.codigo_identificacao}</span></td><td><small>${m.tipo_maquina}</small></td><td><strong>${m.nome_equipamento}</strong></td><td>R$ ${preco}</td><td><small>V: ${m.velocidade_trabalho}<br>A: ${m.avanco_trabalho}</small></td><td><small>${m.capacidade_fisica}</small></td><td>${linkFmt}</td><td><button onclick="carregarMaquinaParaAlterar(${m.id})" class="btn-alt">Alterar</button><button onclick="deletarMaquinaIsolada(${m.id})" class="btn-del">Deletar</button></td>`;
        tbody.appendChild(tr);
    });
}

async function salvarMaquinaIsolada() {
    const id = document.getElementById('maqIsoladaId').value; const tipo_maquina = document.getElementById('maqTipo').value;
    const nome_equipamento = document.getElementById('maqNome').value.trim(); const codigo_identificacao = document.getElementById('maqCodigo').value.trim();
    const preco_compra = parseFloat(document.getElementById('maqPreco').value) || 0; const velocidade_trabalho = document.getElementById('maqVelocidade').value.trim() || 'N/A';
    const avanco_trabalho = document.getElementById('maqAvanco').value.trim() || 'N/A'; const capacidade_fisica = document.getElementById('maqCapacidade').value.trim() || 'N/A';
    const link_mercado = document.getElementById('maqLink').value.trim();
    if (!nome_equipamento || !codigo_identificacao || preco_compra <= 0) { alert("Preencha os campos."); return; }
    const r = await fetch('/api/maquinas_isoladas', { method: id ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, tipo_maquina, nome_equipamento, codigo_identificacao, preco_compra, velocidade_trabalho, avanco_trabalho, capacidade_fisica, link_mercado }) });
    if (r.ok) { document.getElementById('maqIsoladaId').value = ''; document.getElementById('maqNome').value = ''; document.getElementById('maqCodigo').value = ''; document.getElementById('maqLink').value = ''; document.getElementById('btnSalvarMaq').innerText = "Salvar / Registrar Equipamento"; carregarMaquinasIsoladas(); }
}

function carregarMaquinaParaAlterar(id) {
    const m = listaMaquinasIsoladas.find(i => i.id === id); if (!m) return;
    document.getElementById('maqIsoladaId').value = m.id; document.getElementById('maqTipo').value = m.tipo_maquina;
    document.getElementById('maqNome').value = m.nome_equipamento; document.getElementById('maqCodigo').value = m.codigo_identificacao;
    document.getElementById('maqPreco').value = m.preco_compra; document.getElementById('maqVelocidade').value = m.velocidade_trabalho;
    document.getElementById('maqAvanco').value = m.avanco_trabalho; document.getElementById('maqCapacidade').value = m.capacidade_fisica;
    document.getElementById('maqLink').value = m.link_mercado; document.getElementById('btnSalvarMaq').innerText = "Salvar Alterações no Banco";
}

async function deletarMaquinaIsolada(id) {
    if (!confirm("Deletar máquina?")) return;
    const r = await fetch(`/api/maquinas_isoladas/${id}`, { method: 'DELETE' }); if (r.ok) carregarMaquinasIsoladas();
}




// ============================================================================
// MÓDULO 3: ENGENHARIA DE MATERIAIS & ALMOXARIFADO
// ============================================================================
async function carregarMateriaisIsolados() {
    const r = await fetch('/api/materiais_isoladas');
    if (r.ok) { listaMateriaisIsolados = await r.json(); renderizarTabelaMateriaisIsolados(); }
}

function renderizarTabelaMateriaisIsolados() {
    const tbody = document.querySelector('#tabelaMateriaisIsolados tbody'); if (!tbody) return; tbody.innerHTML = '';
    listaMateriaisIsolados.forEach(item => {
        const tr = document.createElement('tr'); const custo = parseFloat(item.custo_unitario).toFixed(2);
        const linkFmt = item.link_fornecedor ? `<a href="${item.link_fornecedor}" target="_blank" style="color:#16a085; font-weight:600; text-decoration:underline;">Ver Cotação 🔗</a>` : 'Não Anexado 📄';
        tr.innerHTML = `<td>#${item.id}</td><td><span class="badge-pcp" style="background-color:#16a085;">${item.tipo_material}</span></td><td><strong>${item.nome_material}</strong></td><td>R$ ${custo} <small>/ ${item.unidade_medida}</small></td><td><small>${item.peso_especifico_kg} kg<br>${item.dimensao_padrao}</small></td><td>${item.indice_perda_percentual}%</td><td>${item.lote_minimo_compra} un</td><td>${linkFmt}</td><td><button onclick="carregarMaterialParaAlterar(${item.id})" class="btn-alt">Alterar</button><button onclick="deletarMaterialIsolado(${item.id})" class="btn-del">Deletar</button></td>`;
        tbody.appendChild(tr);
    });
}

async function salvarMaterialIsolado() {
    const id = document.getElementById('matIsoladoId').value; const nome_material = document.getElementById('matNome').value.trim();
    const tipo_material = document.getElementById('matTipo').value; const custo_unitario = parseFloat(document.getElementById('matCustoUn').value) || 0;
    const unidade_medida = document.getElementById('matUnidade').value; const peso_especifico_kg = parseFloat(document.getElementById('matPeso').value) || 0;
    const dimensao_padrao = document.getElementById('matDimensao').value.trim() || 'N/A'; const indice_perda_percentual = parseFloat(document.getElementById('matPerda').value) || 0;
    const lote_minimo_compra = parseInt(document.getElementById('matLote').value) || 1; const link_fornecedor = document.getElementById('matLink').value.trim();
    if (!nome_material || custo_unitario <= 0) { alert("Preencha os campos."); return; }
    const r = await fetch('/api/materiais_isoladas', { method: id ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id, nome_material, tipo_material, custo_unitario, unidade_medida, peso_especifico_kg, dimensao_padrao, indice_perda_percentual, lote_minimo_compra, link_fornecedor }) });
    if (r.ok) { document.getElementById('matIsoladoId').value = ''; document.getElementById('matNome').value = ''; document.getElementById('matLink').value = ''; document.getElementById('btnSalvarMat').innerText = "Salvar / Registrar Material"; carregarMateriaisIsolados(); }
}

function carregarMaterialParaAlterar(id) {
    const item = listaMateriaisIsolados.find(i => i.id === id); if (!item) return;
    document.getElementById('matIsoladoId').value = item.id; document.getElementById('matNome').value = item.nome_material;
    document.getElementById('matTipo').value = item.tipo_material; document.getElementById('matCustoUn').value = item.custo_unitario;
    document.getElementById('matUnidade').value = item.unidade_medida; document.getElementById('matPeso').value = item.peso_especifico_kg;
    document.getElementById('matDimensao').value = item.dimensao_padrao; document.getElementById('matPerda').value = item.indice_perda_percentual;
    document.getElementById('matLote').value = item.lote_minimo_compra; document.getElementById('matLink').value = item.link_fornecedor;
    document.getElementById('btnSalvarMat').innerText = "Salvar Alterações no Banco";
}

async function deletarMaterialIsolado(id) {
    if (!confirm("Deletar item do almoxarifado?")) return;
    const r = await fetch(`/api/materiais_isoladas/${id}`, { method: 'DELETE' }); if (r.ok) carregarViaSincronia ? carregarMateriaisIsolados() : carregarMateriaisIsolados();
}
