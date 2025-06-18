from django.test import TestCase
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