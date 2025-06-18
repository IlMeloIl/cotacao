import requests
import logging

logger = logging.getLogger(__name__)

class VatcomplyService:
    BASE_URL = "https://api.vatcomply.com/rates"

    def get_rates(self, target_date, symbols=None):
        date_str = target_date.strftime('%Y-%m-%d')
        url = f"{self.BASE_URL}?date={date_str}&base=USD"

        if symbols:
            symbols_str = ','.join(symbols)
            url += f'&symbols={symbols_str}'

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data.get('rates', {})
        except requests.exceptions.RequestException as e :
            logger.error(f"Erro ao acesar API da Vatcomply: {e}")
            return None
