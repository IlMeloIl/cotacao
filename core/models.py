from django.db import models

class Cotacao(models.Model):
    """
    Representa a cotação de uma moeda em relação ao Dólar (USD)
    em uma data específica.
    """
    class Moedas(models.TextChoices):
        BRL = 'BRL', 'Real Brasileiro'
        EUR = 'EUR', 'Euro'
        JPY = 'JPY', 'Iene Japonês'

    moeda = models.CharField(
        max_length=3,
        choices=Moedas.choices,
        help_text="A moeda para a cotação (ex: BRL, EUR, JPY)."
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="O valor da cotação em relação ao USD."
    )
    data = models.DateField(
        help_text="A data da cotação."
    )

    class Meta:
        verbose_name = "Cotação"
        verbose_name_plural = "Cotações"
        ordering = ['-data', 'moeda']
        unique_together = ('moeda', 'data')

    def __str__(self):
        return f"{self.get_moeda_display()} - {self.valor} em {self.data.strftime('%d/%m/%Y')}"