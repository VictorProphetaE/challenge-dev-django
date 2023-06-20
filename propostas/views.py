from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from rest_framework import viewsets, status
from .models import Proposta, CampoDinamico, ValorCampoDinamico
from .serializers import PropostaSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import processar_avaliacao_proposta
from django.http import JsonResponse
from django.db.models import F

class PropostaViewSet(viewsets.ModelViewSet):
    queryset = Proposta.objects.all()
    serializer_class = PropostaSerializer

def index(request):
    return render(request, "propostas/index.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "propostas/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "propostas/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def visualizar_propostas(request):
    # Obtém todas as propostas e campos dinâmicos
    propostas = Proposta.objects.all()
    campos_dinamicos = CampoDinamico.objects.all()

    propostas_with_values = []
    for proposta in propostas:
        valores_campo_dinamico = []
        for campo in campos_dinamicos:
            # Obtém o valor do campo dinâmico da proposta, se existir
            valor_campo = proposta.valores_campo_dinamico.filter(campo_dinamico=campo).first()
            valor = valor_campo.valor if valor_campo is not None else ""
            valores_campo_dinamico.append(valor)
        propostas_with_values.append((proposta, valores_campo_dinamico))

    return render(request, 'propostas/visualizar.html', {'propostas': propostas_with_values, 'campos_dinamicos': campos_dinamicos})

@csrf_exempt
@api_view(['GET', 'POST'])
def enviar_proposta(request):
    if request.method == 'POST':
        # Cria uma nova proposta e definir o status como "Pendente"
        proposta = Proposta()
        proposta.status = 'Pendente'
        proposta.save()

        campos_dinamicos = CampoDinamico.objects.all()
        data = request.data

        campos = data['campos_dinamicos']
        for campo in campos:
            nome_campo = campo['nome']
            valor_campo = campo['valor']
            campo_dinamico = campos_dinamicos.get(nome=nome_campo)
            # Cria um novo valor de campo dinâmico associado à proposta
            ValorCampoDinamico.objects.create(proposta=proposta, campo_dinamico=campo_dinamico, valor=valor_campo)
        # Iniciar a tarefa em segundo plano para processar a avaliação da proposta
        processar_avaliacao_proposta(proposta.id)

        return HttpResponseRedirect(reverse("index"))
    else:
        campos_dinamicos = CampoDinamico.objects.all()
        return render(request, "propostas/proposta.html", {"campos_dinamicos": campos_dinamicos})