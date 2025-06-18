from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PaginaInicialView, dados_grafico, CotacaoViewSet

app_name = 'core'

router = DefaultRouter()
router.register(r'cotacoes', CotacaoViewSet, basename='cotacao')

urlpatterns = [
    path('', PaginaInicialView.as_view(), name='pagina_inicial'),
    path('api/grafico/', dados_grafico, name='dados_grafico'),
    path('api/', include(router.urls)),
]