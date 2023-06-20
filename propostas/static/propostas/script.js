// Função para obter o valor do token CSRF do cookie
function getCSRFToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find((row) => row.startsWith('csrftoken='))
    .split('=')[1];
  return cookieValue;
}

$(document).ready(function() {
  // Função para carregar as propostas utilizando AJAX
  function carregarPropostas() {
      $.ajax({
          url: '/api/propostas/',
          type: 'GET',
          dataType: 'json',
          success: function (data) {
              exibirPropostas(data);
          },
          error: function (xhr, status, error) {
              console.error(error);
          }
      });
  }
  // Função para exibir as propostas na tabela
  function exibirPropostas(propostas) {
    var tabela = $('#propostas-table');
    tabela.empty();
  
    propostas.forEach(function (proposta) {
      var linha = $('<tr>');
  
      // Coluna ID
      var colunaId = $('<td>').text(proposta.id);
      linha.append(colunaId);
  
      // Colunas dos campos dinâmicos
      var camposDinamicos = proposta.campos_dinamicos;
      if (camposDinamicos !== null && Array.isArray(camposDinamicos)) {
        camposDinamicos.forEach(function (campo) {
          var colunaCampoDinamico = $('<td>').text(campo.valor);
          linha.append(colunaCampoDinamico);
        });
      }
  
      tabela.append(linha);
    });
  }  
  // Carregar as propostas ao carregar a página
  carregarPropostas();

  // Manipulador de evento para o envio do formulário de proposta
  $('#proposta-form').submit(function(event) {
    event.preventDefault();
    var proposta = {
      campos_dinamicos: []
    };
    // Iterar sobre os campos do formulário e adicionar os valores não vazios à proposta
    $('input[name^="campo-"]').each(function(index, element) {
      var campoName = $(element).attr('name').split('-')[1];
      var campoValue = $(element).val();
      if (campoValue !== '') { // Verifica se o valor não está vazio
        proposta.campos_dinamicos.push({ nome: campoName, valor: campoValue });
      }
    });
    // Enviar a proposta
    enviarProposta(proposta);
  });
  // Função para enviar a proposta utilizando AJAX
  function enviarProposta(proposta) {
    const csrfToken = getCSRFToken();
    const headers = {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    };
    
    $.ajax({
      url: '/proposta/',
      type: 'POST',
      data: JSON.stringify(proposta),
      headers: headers,
      success: function(response) {
        console.log('Proposta enviada com sucesso:', response);
        carregarPropostas();
      },
      error: function(xhr, status, error) {
        console.error('Erro ao enviar proposta:', error);
        console.log('Detalhes do erro:', xhr.responseText);
      },
    });
  }
});
