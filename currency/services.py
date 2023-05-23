import datetime
import requests

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from currency.models import ExchangeRateProvider, ExchangeRate


class ProvidersService:
    def __init__(self, name, api_url):
        self.name = name
        self.api_url = api_url

    def get_or_create(self):
        provider, created = ExchangeRateProvider.objects.get_or_create(name=self.name, api_url=self.api_url)
        if created:
            # The provider was created because it didn't exist
            print("ExchangeRateProvider created:", provider)
        else:
            print("Existing ExchangeRateProvider retrieved:", provider)

        return provider


class ExchangeRatesService:

    CURRENCIES = ['GBP', 'USD', 'CHF', 'EUR']

    def __init__(self, provider):
        self.provider = provider


class PrivatExchangeRatesService(ExchangeRatesService):

    BANK_NAME = 'Privat Bank'

    def get_rates(self):

        if self.provider.name != self.BANK_NAME:
            raise ObjectDoesNotExist(f'{self.provider.name} not found in DB')

        api_url = self.provider.api_url
        start_date = datetime.datetime(2023, 5, 21)
        end_date = datetime.datetime.now()
        delta = datetime.timedelta(days=1)

        currency_rates = []
        while start_date < end_date:
            currency_rates += self.get_rate(date=start_date, api_url=api_url)
            start_date += delta

        sorted_currency_rates = sorted(currency_rates, key=lambda x: x['date'])

        return sorted_currency_rates

    def get_rate(self, date, api_url):

        params = {
            "date": date.strftime('%d.%m.%Y')
        }

        response = requests.get(api_url, params=params)
        data = response.json()

        rates = data['exchangeRate']
        currency_rates = []
        base_currency = data['baseCurrencyLit']
        date = data['date']
        for r in rates:
            if r['currency'] not in self.CURRENCIES:
                continue

            currency_rates.append(
                {
                    'base_currency': base_currency,
                    'currency': r['currency'],
                    'buy_rate': r['purchaseRate'],
                    'sale_rate': r['saleRate'],
                    'date': date

                }
            )
        return currency_rates

    def persist_currency_rates(self, objects):
        currency_rates = []
        for cu_rate in objects:
            check_rate = (
                ExchangeRate.objects
                .filter(
                    currency=cu_rate.get('currency'),
                    date=cu_rate.get('date')
                )
                .first()
            )

            if check_rate:
                continue

            check_rate = ExchangeRate(
                base_currency=cu_rate.get('base_currency'),
                currency=cu_rate.get('currency'),
                buy_rate=cu_rate.get('buy_rate'),
                sale_rate=cu_rate.get('sale_rate'),
                date=cu_rate.get('date'),
                provider_id=self.provider.id
            )
            check_rate.save()
            currency_rates.append(model_to_dict(check_rate))

        return currency_rates
