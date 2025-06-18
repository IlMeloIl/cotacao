from django.core.management.base import BaseCommand, CommandError
from datetime import date, timedelta, datetime

from core.models import Cotacao
from core.services import VatcomplyService

class Command(BaseCommand):
    help = 'Busca e salva as cotações de moedas (BRL, EUR, JPY) para o dia atual.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data',
            help='Busca cotações para uma data específica (formato AAAA-MM-DD).'
        )
        parser.add_argument(
            '--inicio',
            help='Data de início para busca em um intervalo (formato AAAA-MM-DD).'
        )
        parser.add_argument(
            '--fim',
            help='Data de fim para busca em um intervalo (formato AAAA-MM-DD).'
        )

    def handle(self, *args, **options):
        self.service = VatcomplyService()
        self.moedas_desejadas = ['BRL', 'EUR', 'JPY']
        
        data_str = options.get('data')
        inicio_str = options.get('inicio')
        fim_str = options.get('fim')

        if data_str:
            target_date = datetime.strptime(data_str, '%Y-%m-%d').date()
            self.buscar_e_salvar_para_data(target_date)
        elif inicio_str and fim_str:
            start_date = datetime.strptime(inicio_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(fim_str, '%Y-%m-%d').date()

            if start_date > end_date:
                raise CommandError('A data de início não pode ser posterior à data de fim.')
            
            current_date = start_date
            while current_date <= end_date:
                self.buscar_e_salvar_para_data(current_date)
                current_date += timedelta(days=1)
        else:
            self.buscar_e_salvar_para_data(date.today())
        
        self.stdout.write(self.style.SUCCESS('Operação concluída com sucesso.'))
    
    def buscar_e_salvar_para_data(self, target_date):
        self.stdout.write(self.style.NOTICE(f'Buscando cotações para {target_date.strftime("%d-%m-%Y")}...'))

        rates = self.service.get_rates(target_date, symbols=self.moedas_desejadas)

        if not rates:
            self.stdout.write(self.style.ERROR(f'Não foi possível obter cotações para {target_date.strftime("%d-%m-%Y")}.'))
            return
        
        for moeda_sigla, valor in rates.items():
            _, created = Cotacao.objects.update_or_create(
                moeda=moeda_sigla,
                data=target_date,
                defaults={'valor': valor}
            )
            if created:
                self.stdout.write(f'  -> Cotação para {moeda_sigla} criada: {valor}')
            else:
                self.stdout.write(f'  -> Cotação para {moeda_sigla} atualizada: {valor}')