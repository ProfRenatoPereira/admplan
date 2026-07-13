let registrosImobiliarios = [];

document.addEventListener('DOMContentLoaded', () => {
    // Menu Hamburger Responsivo padrão corporativo
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            const exp = menuToggle.getAttribute('aria-expanded') === 'true';
            menuToggle.setAttribute('aria-expanded', !exp);
            navMenu.classList.toggle('active');
        });
    }

    // ARQUITETURA ISOLADA: Só roda se a tabela específica do imóvel existir na tela ativa
    if (document.getElementById('tabelaImobiliarioIsolado')) {
        carregarImobiliarioIsolado();
    }
});

// Acessibilidade Padrão do Sistema
function toggleContraste() { document.body.classList.toggle('alto-contraste'); }
let tamanhoFonteAtual = 100;
function alterarFonte(dir) {
    tamanhoFonteAtual += (dir * 10);
    if (tamanhoFonteAtual >= 80 && tamanhoFonteAtual <= 140) document.documentElement.style.fontSize = `${tamanhoFonteAtual}%`;
}

// FUNÇÃO DE LEITURA: Busca do PostgreSQL e monta a tabela atualizada na hora
async function carregarImobiliarioIsolado() {
    const response = await fetch('/api/imobiliario_isolado');
    if (response.ok) {
        registrosImobiliarios = await response.json();
        renderizarTabelaImobiliarioIsolado();
    }
}
function renderizarTabelaImobiliarioIsolado() {
    const tbody = document.querySelector('#tabelaImobiliarioIsolado tbody');
    if (!tbody) return; tbody.innerHTML = '';

    registrosImobiliarios.forEach(item => {
        const tr = document.createElement('tr');
        const capital = parseFloat(item.valor_capital).toFixed(2);
        
        // Calcula visualmente os 50% do aluguel com a correção para mostrar na célula
        const aluguelSimulado = ((parseFloat(item.valor_aluguel_mercado) * 0.5) * (1 + (parseFloat(item.indice_correcao) / 100))).toFixed(2);
        const custoMin = parseFloat(item.custo_minuto_instalacao).toFixed(4);
        const meses = parseFloat(item.meses_retorno).toFixed(1);

        tr.innerHTML = `
            <td>#${item.id}</td>
            <td><strong>${item.descricao}</strong></td>
            <td>R$ ${capital}</td>
            <td style="color:var(--accent); font-weight:bold;">R$ ${aluguelSimulado}</td>
            <td>R$ ${custoMin}</td>
            <td><strong>${meses} meses</strong></td>
            <td>
                <button onclick="carregarParaAlterar(${item.id})" class="btn-alt">Alterar</button>
                <button onclick="deletarRegistroIsolado(${item.id})" class="btn-del">Deletar</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function salvarImobiliarioIsolado() {
    const id = document.getElementById('imoIsoladoId').value;
    const descricao = document.getElementById('imoDescricao').value.trim();
    const valor_capital = parseFloat(document.getElementById('imoCapital').value) || 0;
    const valor_aluguel_mercado = parseFloat(document.getElementById('imoAluguel').value) || 0;
    const indice_correcao = parseFloat(document.getElementById('imoIndice').value) || 0;
    const minutos_operacionais_ano = parseInt(document.getElementById('imoMinutos').value) || 144000;

    if (!descricao || valor_capital <= 0) { alert("Preencha a identificação e o valor capital do imóvel."); return; }
    const metodo = id ? 'PUT' : 'POST';

    const response = await fetch('/api/imobiliario_isolado', {
        method: metodo,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, descricao, valor_capital, valor_aluguel_mercado, indice_correcao, minutos_operacionais_ano })
    });

    if (response.ok) {
        document.getElementById('imoIsoladoId').value = '';
        document.getElementById('imoDescricao').value = '';
        document.getElementById('btnSalvarImo').innerText = "Salvar / Registrar Instalação";
        carregarImobiliarioIsolado();
    }
}

function carregarParaAlterar(id) {
    const item = registrosImobiliarios.find(i => i.id === id);
    if (!item) return;

    document.getElementById('imoIsoladoId').value = item.id;
    document.getElementById('imoDescricao').value = item.descricao;
    document.getElementById('imoCapital').value = item.valor_capital;
    document.getElementById('imoAluguel').value = item.valor_aluguel_mercado;
    document.getElementById('imoIndice').value = item.indice_correcao;
    document.getElementById('imoMinutos').value = item.minutos_operacionais;
    
    document.getElementById('btnSalvarImo').innerText = "Salvar Alterações no Banco";
}

async function deletarRegistroIsolado(id) {
    if (!confirm("Confirmar a exclusão permanente deste imóvel do banco de dados do Render?")) return;
    const response = await fetch(`/api/imobiliario_isolado/${id}`, { method: 'DELETE' });
    if (response.ok) {
        carregarImobiliarioIsolado();
    }
}
