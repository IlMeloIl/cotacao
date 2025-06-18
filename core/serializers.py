from rest_framework import serializers
from .models import Cotacao

class CotacaoSerializer(serializers.ModelSerializer):
    moeda_display = serializers.CharField(source='get_moeda_display', read_only=True)

    class Meta:
        model = Cotacao
        fields = '__all__'