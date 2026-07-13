// Aguarda o carregamento total da página HTML
document.addEventListener('DOMContentLoaded', () => {
    inicializarFormularios();
    configurarPrecosInternet();
});

// Adiciona validações e interceptações em todos os formulários da aplicação
function inicializarFormularios() {
    const formularios = document.querySelectorAll('form');
    
    formularios.forEach(form => {
        form.addEventListener('submit', function(event) {
            // Executa validações de segurança dos campos
            if (!validarCamposObrigatorios(this)) {
                event.preventDefault(); // Impede o envio se houver erro
                alert('Por favor, preencha todos os campos obrigatórios corretamente.');
            }
        });
    });
}


// Garante que valores de engenharia e finanças sejam válidos
function validarCamposObrigatorios(formulario) {
    let formularioValido = true;
    const inputsNumericos = formulario.querySelectorAll('input[type="number"]');
    
    inputsNumericos.forEach(input => {
        const valor = parseFloat(input.value);
        // Regra de Negócio: Preços, tempos e custos não podem ser negativos
        if (valor < 0) {
            input.style.borderColor = 'red';
            formularioValido = false;
        } else {
            input.style.borderColor = '';
        }
    });
    
    return formularioValido;
}



// Simula a busca de tabelas de preços e tarifas pela internet
function configurarPrecosInternet() {
    const linksInternet = document.querySelectorAll('a[href^="http"]');
    
    linksInternet.forEach(link => {
        link.addEventListener('click', function(e) {
            console.log(`Buscando catálogo de preços atualizado em: ${this.href}`);
            // Aqui pode ser injetado um fetch() futuro para APIs de marketplaces ou SEFAZ
        });
    });
}

// Função utilitária para formatar valores no padrão de moeda brasileira (R$)
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}
