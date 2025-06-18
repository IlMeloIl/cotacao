# core/urls.py

from django.urls import path
from .views import PaginaInicialView, dados_grafico

app_name = 'core'

urlpatterns = [
    path('', PaginaInicialView.as_view(), name='pagina_inicial'),
    path('api/cotacoes/', dados_grafico, name='dados_grafico'),
]