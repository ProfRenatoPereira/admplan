let parqueMaquinas = [];
let listaMateriaisBanco = [];
let listaProcessosPcp = [];
let carteiraPedidosVendas = [];

document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            const expandido = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', !expandido);
            navMenu.classList.toggle('active');
        });
    }
    if (document.getElementById('tabelaMaquinas')) carregarMaquinasDoServidor();
    if (document.getElementById('tabelaMateriais')) carregarMateriaisDoServidor();
    if (document.getElementById('procSelecaoMaquina')) carregarProcessosEAtivosFabrica();
    if (document.getElementById('vendaSelecaoProduto')) carregarModuloVendasEPlanejamento();
    if (document.getElementById('custoTotal')) carregarEMotorCustoGlobal();
    if (document.getElementById('imoTerreno')) carregarDadosImovelExistente();
});

function toggleContraste() { document.body.classList.toggle('alto-contraste'); }
let tamanhoFonteAtual = 100;
function alterarFonte(direcao) {
    tamanhoFonteAtual += (direcao * 10);
    if (tamanhoFonteAtual >= 80 && tamanhoFonteAtual <= 140) document.documentElement.style.fontSize = `${tamanhoFonteAtual}%`;
}
function emitirAudioTexto(texto) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const m = new SpeechSynthesisUtterance(texto); m.lang = 'pt-BR'; window.speechSynthesis.speak(m);
    }
}

async function carregarDadosImovelExistente() {
    const response = await fetch('/api/imobiliario');
    if (response.ok) {
        const imovel = await response.json();
        if (imovel.valor_terreno) {
            document.getElementById('imoTerreno').value = imovel.valor_terreno;
            document.getElementById('imoEdificacao').value = imovel.custo_edificacao;
            document.getElementById('imoImpostos').value = imovel.impostos_transferencia;
        }
    }
}

async function calcularCustosImobiliarios() {
    const valor_terreno = parseFloat(document.getElementById('imoTerreno').value) || 0;
    const custo_edificacao = parseFloat(document.getElementById('imoEdificacao').value) || 0;
    const impostos_anuais = parseFloat(document.getElementById('imoImpostos').value) || 0;
    const vida_util_anos = parseInt(document.getElementById('imoVidaUtil').value) || 20;
    const minutos_operacionais_ano = parseInt(document.getElementById('imoHorasAno').value) || 144000;

    const response = await fetch('/api/imobiliario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ valor_terreno, custo_edificacao, impostos_anuais, vida_util_anos, minutos_operacionais_ano })
    });
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('custoMinutoImobiliario', data.custoMinutoInstalacao);
        localStorage.setItem('totalInvestidoEstrutura', (valor_terreno + custo_edificacao).toString());
        const box = document.getElementById('resultadoImobiliario');
        if (box) { box.style.display = 'block'; box.innerHTML = `<p>Custo Planta: R$ ${data.custoMinutoInstalacao} / min.</p>`; }
        emitirAudioTexto("Custos imobiliarios salvos.");
    }
}
async function carregarMaquinasDoServidor() {
    const response = await fetch('/api/maquinas');
    if (response.ok) { parqueMaquinas = await response.json(); renderizarTabelaMaquinas(); }
}

async function adicionarMaquinaServidor() {
    const id_maquina = document.getElementById('maquinaIdOculto').value;
    const nome = document.getElementById('maquinaNome').value.trim();
    const preco = parseFloat(document.getElementById('maquinaPreco').value) || 0;
    const vidaUtil = parseInt(document.getElementById('maquinaVidaUtil').value) || 1;
    const valorRevenda = parseFloat(document.getElementById('maquinaValorRevenda').value) || 0;
    const manutencao = parseFloat(document.getElementById('maquinaManutencao').value) || 0;
    const minutos_ativos_ano = parseInt(document.getElementById('maquinaHorasAno').value) || 144000;
    const potencia_kw = parseFloat(document.getElementById('maquinaPotencia').value) || 0;
    const tarifa_kwh = parseFloat(document.getElementById('maquinaTarifa').value) || 0;
    const data_aquisicao = document.getElementById('maquinaAquisicao').value;
    const data_manutencao = document.getElementById('maquinaPrev').value;
    const diametro_mm = parseFloat(document.getElementById('maquinaDiametro').value) || 0;
    const comprimento_mm = parseFloat(document.getElementById('maquinaComprimento').value) || 0;

    if (!nome || preco <= 0) { alert("Preencha o ativo."); return; }
    const metodo = id_maquina ? 'PUT' : 'POST';

    const response = await fetch('/api/maquinas', {
        method: metodo,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: id_maquina, nome, preco, vida_util: vidaUtil, valor_revenda: valorRevenda, manutencao, minutos_ativos_ano, potencia_kw, tarifa_kwh, data_aquisicao, data_manutencao, diametro_mm, comprimento_mm })
    });
    if (response.ok) { limparFormularioMaquinas(); carregarMaquinasDoServidor(); emitirAudioTexto("Ativo processado."); }
}

function renderizarTabelaMaquinas() {
    const tbody = document.querySelector('#tabelaMaquinas tbody'); if (!tbody) return; tbody.innerHTML = '';
    parqueMaquinas.forEach(m => {
        const tr = document.createElement('tr'); const dt = m.data_manutencao_preventiva ? m.data_manutencao_preventiva.substring(0,10) : 'N/A';
        tr.innerHTML = `<td><strong>${m.nome_maquina}</strong></td><td>Ø ${m.diametro_trabalho_mm} x ${m.comprimento_trabalho_mm} mm</td><td>${m.potencia_kw} kW</td><td>${dt}</td><td>R$ ${parseFloat(m.custo_minuto_maquina).toFixed(4)}</td><td><button onclick="carregarAtivoParaEdicao(${m.id})" class="btn-alt">Alterar</button><button onclick="deletarAtivoServidor(${m.id})" class="btn-del">Deletar</button></td>`;
        tbody.appendChild(tr);
    });
}

async function deletarAtivoServidor(id) {
    if (!confirm("Deletar ativo?")) return;
    const response = await fetch(`/api/maquinas/${id}`, { method: 'DELETE' }); if (response.ok) carregarMaquinasDoServidor();
}

function carregarAtivoParaEdicao(id) {
    const m = parqueMaquinas.find(item => item.id === id); if (!m) return;
    document.getElementById('maquinaIdOculto').value = m.id; document.getElementById('maquinaNome').value = m.nome_maquina;
    document.getElementById('maquinaPreco').value = m.preco_compra; document.getElementById('maquinaVidaUtil').value = m.tempo_vida_util_anos;
    document.getElementById('maquinaValorRevenda').value = m.valor_revenda_estimado; document.getElementById('maquinaManutencao').value = m.custo_manutencao_anual;
    document.getElementById('maquinaHorasAno').value = m.minutos_ativos_ano; document.getElementById('maquinaPotencia').value = m.potencia_kw;
    document.getElementById('maquinaTarifa').value = m.tarifa_kwh; document.getElementById('maquinaAquisicao').value = m.data_aquisicao.substring(0,10);
    document.getElementById('maquinaPrev').value = m.data_manutencao_preventiva.substring(0,10);
    document.getElementById('maquinaDiametro').value = m.diametro_trabalho_mm; document.getElementById('maquinaComprimento').value = m.comprimento_trabalho_mm;
    document.getElementById('btnSalvarAtivo').innerText = "Salvar Alteracoes";
}

function limparFormularioMaquinas() { document.getElementById('maquinaIdOculto').value = ''; document.getElementById('maquinaNome').value = ''; document.getElementById('btnSalvarAtivo').innerText = "Salvar e Registrar Ativo"; }

async function carregarMateriaisDoServidor() {
    const response = await fetch('/api/materiais'); if (response.ok) { listaMateriaisBanco = await response.json(); renderizarTabelaMateriais(); }
}

async function adicionarMaterialServidor() {
    const id_mat = document.getElementById('materialIdOculto').value; const nome = document.getElementById('materialNome').value.trim();
    const tipo = document.getElementById('materialTipo').value; const custo_unitario = parseFloat(document.getElementById('materialCustoUn').value) || 0;
    const unidade_medida = document.getElementById('materialUnidade').value;
    if (!nome || custo_unitario <= 0) return; const metodo = id_mat ? 'PUT' : 'POST';
    const response = await fetch('/api/materiais', { method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: id_mat, nome, tipo, custo_unitario, unidade_medida }) });
    if (response.ok) { document.getElementById('materialIdOculto').value = ''; document.getElementById('materialNome').value = ''; document.getElementById('btnSalvarMaterial').innerText = "Salvar / Adicionar Item"; carregarMateriaisDoServidor(); }
}

function renderizarTabelaMateriais() {
    const tbody = document.querySelector('#tabelaMateriais tbody'); if (!tbody) return; tbody.innerHTML = '';
    listaMateriaisBanco.forEach(m => {
        const tr = document.createElement('tr'); tr.innerHTML = `<td>${m.nome_material}</td><td>${m.tipo_material}</td><td>R$ ${parseFloat(m.custo_unitario).toFixed(2)}</td><td>${m.unidade_medida}</td><td><button onclick="carregarMaterialEdicao(${m.id})" class="btn-alt">Alterar</button><button onclick="deletarMaterialServidor(${m.id})" class="btn-del">Deletar</button></td>`; tbody.appendChild(tr);
    });
}

async function deletarMaterialServidor(id) {
    if (!confirm("Excluir item?")) return;
    const response = await fetch(`/api/materiais/${id}`, { method: 'DELETE' }); if (response.ok) carregarMateriaisDoServidor();
}

function carregarMaterialEdicao(id) {
    const m = listaMateriaisBanco.find(i => i.id === id); document.getElementById('materialIdOculto').value = m.id;
    document.getElementById('materialNome').value = m.nome_material; document.getElementById('materialTipo').value = m.tipo_material;
    document.getElementById('materialCustoUn').value = m.custo_unitario; document.getElementById('materialUnidade').value = m.unidade_medida;
    document.getElementById('btnSalvarMaterial').innerText = "Salvar Alteracoes";
}
async function carregarProcessosEAtivosFabrica() {
    const select = document.getElementById('procSelecaoMaquina'); if (!select) return;
    const response = await fetch('/api/maquinas');
    if (response.ok) {
        parqueMaquinas = await response.json(); select.innerHTML = '<option value="">-- Selecione uma máquina --</option>';
        parqueMaquinas.forEach(m => { const o = document.createElement('option'); o.value = m.id; o.textContent = m.nome_maquina; select.appendChild(o); });
    }
    carregarRoteirosPcpDoServidor();
}

async function carregarRoteirosPcpDoServidor() {
    const response = await fetch('/api/processos'); if (response.ok) { listaProcessosPcp = await response.json(); renderizarTabelaProcessosPcp(); }
}

async function adicionarProcessoPcpServidor() {
    const id_proc = document.getElementById('processoIdOculto').value; const codigo_produto = document.getElementById('procCodigoProd').value.trim();
    const nome_produto = document.getElementById('procNomeProd').value.trim(); const maquina_id = document.getElementById('procSelecaoMaquina').value;
    const tempo_ciclo_min = parseFloat(document.getElementById('procTempoCiclo').value) || 0; const tempo_setup_min = parseFloat(document.getElementById('procTempoSetup').value) || 0;
    const lote_padrao = parseInt(document.getElementById('procLotePadrao').value) || 100;
    if (!codigo_produto || !nome_produto || !maquina_id) return; const metodo = id_proc ? 'PUT' : 'POST';
    const response = await fetch('/api/processos', { method: metodo, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: id_proc, codigo_produto, nome_produto, maquina_id, tempo_ciclo_min, tempo_setup_min, lote_padrao }) });
    if (response.ok) { document.getElementById('processoIdOculto').value = ''; document.getElementById('procCodigoProd').value = ''; document.getElementById('procNomeProd').value = ''; document.getElementById('btnSalvarProcesso').innerText = "Salvar e Codificar Produto"; carregarRoteirosPcpDoServidor(); }
}

function renderizarTabelaProcessosPcp() {
    const tbody = document.querySelector('#tabelaProcessos tbody'); if (!tbody) return; tbody.innerHTML = '';
    listaProcessosPcp.forEach(p => {
        const tr = document.createElement('tr'); tr.innerHTML = `<td><strong>${p.codigo_produto}</strong></td><td>${p.nome_produto}</td><td>${p.nome_maquina}</td><td>${p.tempo_cycle_min} min</td><td>${p.tempo_setup_min} min</td><td><button onclick="carregarProcessoEdicao(${p.id})" class="btn-alt">Alterar</button><button onclick="deletarProcessoServidor(${p.id})" class="btn-del">Deletar</button></td>`; tbody.appendChild(tr);
    });
}

async function deletarProcessoServidor(id) {
    if (!confirm("Excluir roteiro?")) return;
    const response = await fetch(`/api/processos/${id}`, { method: 'DELETE' }); if (response.ok) carregarRoteirosPcpDoServidor();
}

function carregarProcessoEdicao(id) {
    const p = listaProcessosPcp.find(i => i.id === id); document.getElementById('processoIdOculto').value = p.id;
    document.getElementById('procCodigoProd').value = p.codigo_produto; document.getElementById('procNomeProd').value = p.nome_produto;
    document.getElementById('procSelecaoMaquina').value = p.maquina_id; document.getElementById('procTempoCiclo').value = p.tempo_cycle_min;
    document.getElementById('procTempoSetup').value = p.tempo_setup_min; document.getElementById('procLotePadrao').value = p.lote_padrao;
    document.getElementById('btnSalvarProcesso').innerText = "Salvar Alteracoes";
}

function carregarEMotorCustoGlobal() { const t = parseFloat(localStorage.getItem('custoTotalProcessos')) || 150; document.getElementById('custoTotal').value = t.toFixed(2); }
function ajustarMargemPorCanal() { const c = document.getElementById('canalPreco').value; document.getElementById('lucro').value = c === 'atacado' ? "15" : "25"; }

async function calcularPrecovenda() {
    const custo_total = document.getElementById('custoTotal').value; const margem_lucro = document.getElementById('lucro').value; const impostos = document.getElementById('impostosInput').value;
    const response = await fetch('/api/calculo-markup', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ custo_total, margem_lucro, impostos }) });
    if (response.ok) { const d = await response.json(); localStorage.setItem('lucroPorPecaGlobal', (d.preco_venda - parseFloat(custo_total)).toString()); document.getElementById('resultado').innerHTML = `<h3>Preço Final: R$ ${d.preco_venda}</h3>`; document.getElementById('resultado').style.display = 'block'; }
}

async function carregarModuloVendasEPlanejamento() {
    const select = document.getElementById('vendaSelecaoProduto'); if (!select) return;
    const response = await fetch('/api/processos');
    if (response.ok) {
        listaProcessosPcp = await response.json(); select.innerHTML = '<option value="">-- Selecione o Produto --</option>';
        listaProcessosPcp.forEach(p => { const o = document.createElement('option'); o.value = p.id; o.textContent = `[${p.codigo_produto}] - ${p.nome_produto}`; select.appendChild(o); });
    }
    carregarPedidosVendasDoServidor();
}

async function carregarPedidosVendasDoServidor() { const response = await fetch('/api/vendas'); if (response.ok) { carteiraPedidosVendas = await response.json(); renderizarTabelaPedidosVendas(); } }

async function emitirPedidoComercialVenda() {
    const pid = document.getElementById('vendaSelecaoProduto').value; const q = parseInt(document.getElementById('vendaQuantidade').value) || 0; const c = document.getElementById('vendaCliente').value.trim();
    if (!pid || q <= 0 || !c) return;
    const response = await fetch('/api/vendas', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ processo_id: pid, quantidade: q, cliente: c }) });
    if (response.ok) { document.getElementById('vendaCliente').value = ''; carregarPedidosVendasDoServidor(); }
}

function renderizarTabelaPedidosVendas() {
    const tbody = document.querySelector('#tabelaVendas tbody'); if (!tbody) return; tbody.innerHTML = '';
    carteiraPedidosVendas.forEach(v => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td><strong>PV-${v.id}</strong></td><td>${v.cliente_nome}</td><td>[${v.codigo_produto}] - ${v.nome_produto}</td><td>${v.quantidade_pedida} un</td><td><span class='badge-pcp'>${v.carga_minutos_pcp} Minutos</span></td><td><button onclick="deletarPedidoVenda(${v.id})" class="btn-del">X</button></td>`;
        tbody.appendChild(tr);
    });
}

async function deletarPedidoVenda(id) { if (!confirm("Cancelar?")) return; const r = await fetch(`/api/vendas/${id}`, { method: 'DELETE' }); if (r.ok) carregarPedidosVendasDoServidor(); }

async function calcularTempoRetorno() {
    const vol = parseInt(document.getElementById('retVendasMensais').value) || 0; const des = parseFloat(document.getElementById('retDespesasFixas').value) || 0;
    const invImo = parseFloat(localStorage.getItem('totalInvestidoEstrutura')) || 0; const r = await fetch('/api/maquinas'); let totMaq = 0;
    if (r.ok) { const m = await r.json(); totMaq = m.reduce((acc, c) => acc + parseFloat(c.preco_compra || 0), 0); }
    const totInv = invImo + totMaq; const luc = parseFloat(localStorage.getItem('lucroPorPecaGlobal')) || 0;
    const box = document.getElementById('resultadoRetorno'); if (!box) return; box.style.display = "block";
    if (totInv <= 0 || luc <= 0) { box.innerHTML = "<span style='color:red;'>Preencha os módulos anteriores.</span>"; return; }
    const liq = (vol * luc) - des; if (liq <= 0) { box.innerHTML = "<span style='color:red;'>Lucro insuficiente.</span>"; return; }
    box.innerHTML = `<p>Investimento de R$ ${totInv.toFixed(2)} retornará em <strong>${(totInv / liq).toFixed(1)} meses</strong>.</p>`;
}
