import django_filters
from .models import Cotacao

class CotacaoFilter(django_filters.FilterSet):
    data_inicio = django_filters.DateFilter(field_name='data', lookup_expr='gte')
    data_fim = django_filters.DateFilter(field_name='data', lookup_expr='lte')

    class Meta:
        model = Cotacao

        fields = ['moeda', 'data_inicio', 'data_fim']