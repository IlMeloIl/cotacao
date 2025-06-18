from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, Mock
from datetime import date
import requests

from .models import Cotacao
from .services import VatcomplyService

class CoreAppTests(TestCase):
    def setUp(self):
        self.service = VatcomplyService()

    def test_create_cotacao_model(self):
        cotacao = Cotacao.objects.create(
            moeda='BRL',
            valor='5.6439',
            data=date(2025, 5, 20)
        )
        self.assertIsNotNone(cotacao)
        self.assertEqual(cotacao.moeda, 'BRL')
        self.assertEqual(cotacao.valor, '5.6439')
        self.assertEqual(str(cotacao), 'Real Brasileiro - 5.6439 em 20/05/2025')
        self.assertEqual(Cotacao.objects.count(), 1)

    @patch('core.services.requests.get')
    def test_get_rates_success(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "base": "USD",
            "date": "2025-05-20",
            "rates": {
                "BRL": 5.6439,
                "EUR": 0.8896,
                "JPY": 144.6401
            }
        }
        mock_get.return_value = mock_response

        target_date = date(2025, 5, 20)
        symbols_request = ['BRL', 'EUR', 'JPY']
        rates = self.service.get_rates(target_date, symbols=symbols_request)
        
        self.assertIsNotNone(rates)
        self.assertEqual(rates['BRL'], 5.6439)
        self.assertEqual(rates['EUR'], 0.8896)
        self.assertEqual(rates['JPY'], 144.6401)

        expected_url = "https://api.vatcomply.com/rates?date=2025-05-20&base=USD&symbols=BRL,EUR,JPY"
        mock_get.assert_called_once_with(expected_url, timeout=10)

    @patch('core.services.requests.get')
    def test_get_rates_api_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Erro de conexão")

        target_date = date(2025, 5, 20)
        rates = self.service.get_rates(target_date)

        self.assertIsNone(rates)

class DadosGraficoAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('core:dados_grafico')

        Cotacao.objects.create(moeda='BRL', valor='5.10', data=date(2025, 6, 9)) # Seg
        Cotacao.objects.create(moeda='EUR', valor='0.90', data=date(2025, 6, 9)) # Seg
        Cotacao.objects.create(moeda='BRL', valor='5.12', data=date(2025, 6, 10)) # Ter
        Cotacao.objects.create(moeda='BRL', valor='5.15', data=date(2025, 6, 11)) # Qua
        Cotacao.objects.create(moeda='BRL', valor='5.13', data=date(2025, 6, 12)) # Qui
        Cotacao.objects.create(moeda='BRL', valor='5.18', data=date(2025, 6, 13)) # Sex

    def test_requisicao_com_periodo_valido(self):
        params = {
            'data_inicio': '2025-06-09',
            'data_fim': '2025-06-11',
            'moedas': 'BRL',
        }

        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)

        dados = response.json()
        self.assertIsNotNone(dados)
        self.assertEqual(len(dados), 3)
        self.assertEqual(dados[0]['moeda'], 'BRL')
        self.assertEqual(dados[0]['valor'], '5.1000')

    def test_requisicao_com_periodo_invalido(self):
        params = {
            'data_inicio': '2025-06-09',
            'data_fim': '2025-06-16',
            'moedas': 'BRL',
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 400)

        erro = response.json()
        self.assertIn('error', erro)
        self.assertEqual(erro['error'], 'O periodo selecionado tem 6 dias uteis, o maximo permitido: 5.')

    def test_requisicao_para_periodo_sem_dados(self):
        params = {
            'data_inicio': '2024-01-01',
            'data_fim': '2024-01-05',
            'moedas': 'BRL'
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)

        dados = response.json()
        self.assertEqual(len(dados), 0)
        self.assertEqual(dados, [])

    def test_requisicao_com_parametros_faltando(self):
        params = {
            'data_inicio': '2025-06-16',
        }
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 400)

        erro = response.json()
        self.assertIn('error', erro)
        self.assertEqual(erro['error'], 'Parametros data_inicio, data_fim e moedas sao obrigatorios.')