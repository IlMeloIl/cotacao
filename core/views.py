from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Min, Max
from datetime import datetime, timedelta
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Cotacao
from .serializers import CotacaoSerializer
from .filters import CotacaoFilter

class PaginaInicialView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        datas_disponiveis = Cotacao.objects.aggregate(
            min_data=Min('data'),
            max_data=Max('data')
        )

        min_data = datas_disponiveis.get('min_data')
        max_data = datas_disponiveis.get('max_data')

        if min_data:
            context['min_data_disponivel'] = min_data.strftime('%Y-%m-%d')
        if max_data:
            context['max_data_disponivel'] = max_data.strftime('%Y-%m-%d')

        return context

def dados_grafico(request):
    data_inicio_str = request.GET.get('data_inicio')
    data_fim_str = request.GET.get('data_fim')
    moedas_str = request.GET.get('moedas')

    if not all([data_inicio_str, data_fim_str, moedas_str]):
        return JsonResponse(
            {'error': 'Parametros data_inicio, data_fim e moedas sao obrigatorios.'},
            status=400
        )
    
    try:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        moedas_lista = [moeda.strip().upper() for moeda in moedas_str.split(',')]
    except ValueError:
        return JsonResponse(
            {'error': 'Formato de data ou moeda invalido.'},
            status=400
        )

    # limita consulta para no maximo 5 dias uteis
    dias_uteis = 0
    data_atual = data_inicio
    while data_atual <= data_fim:
        if data_atual.weekday() < 5:
            dias_uteis += 1
        data_atual += timedelta(days=1)
    
    if dias_uteis > 5:
        return JsonResponse(
            {'error': f'O periodo selecionado tem {dias_uteis} dias uteis, o maximo permitido: 5.'},
            status=400
        )

    cotacoes = Cotacao.objects.filter(
        data__range=[data_inicio, data_fim],
        moeda__in=moedas_lista
    ).order_by('data').values('data', 'moeda', 'valor')

    dados_formatados = list(cotacoes)
    return JsonResponse(dados_formatados, safe=False)

class CotacaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cotacao.objects.all().order_by('-data', 'moeda')
    serializer_class = CotacaoSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = CotacaoFilter