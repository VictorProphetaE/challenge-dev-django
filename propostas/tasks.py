import random
from celery import shared_task
from .models import Proposta

@shared_task
def processar_avaliacao_proposta(proposta_id):
    # Obtém a instância da proposta com base no ID fornecido
    proposta = Proposta.objects.get(id=proposta_id)
    # Define as opções de status da proposta
    opcoes_status = ['Negada', 'Aprovada']
    # Escolhe aleatoriamente uma opção de status da lista
    proposta.status = random.choice(opcoes_status)
    
    proposta.save()