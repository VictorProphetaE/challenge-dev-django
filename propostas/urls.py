from django.urls import path, include
from rest_framework import routers
from . import views

# Cria uma instância do router padrão do Django REST Framework
router = routers.DefaultRouter()
# Registra a viewset PropostaViewSet no router
router.register(r'propostas', views.PropostaViewSet)

# Configura as URLs do aplicativo
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path('visualizar/', views.visualizar_propostas, name='visualizar'),
    path('proposta/', views.enviar_proposta, name='proposta'),
    # URLs da API RESTful, incluindo as rotas definidas no router
    path('api/', include(router.urls)),
]