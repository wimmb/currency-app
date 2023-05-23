import datetime
import requests

from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from currency.models import ExchangeRateProvider, ExchangeRate


class ProvidersService:

    @staticmethod
    def get_provider_by_name(name):

        privat = (
            ExchangeRateProvider.objects
            .filter(
                name=name
            )
            .first()
        )

        return privat

    def create_provider(self, data):

        provider = (
            ExchangeRateProvider.objects
            .filter(
                name=data["name"]
            )
            .first()
        )

        if not provider:
            provider = ExchangeRateProvider(
                name=data["name"],
                api_url=data["api_url"]
            )
            provider.save()

        return provider


class PrivatExchangeRatesService:

    CURRENCIES = ['GBP', 'USD', 'CHF', 'EUR']
    BANK_NAME = 'Privat Bank'

    def get_rates(self):

        privat = ProvidersService.get_provider_by_name(self.BANK_NAME)

        if not privat:
            raise ObjectDoesNotExist(f'{self.BANK_NAME} not found in DB')

        provider_id = privat.id
        api_url = privat.api_url
        start_date = datetime.datetime(2023, 5, 21)
        end_date = datetime.datetime.now()
        delta = datetime.timedelta(days=1)

        currency_rates = []
        while start_date < end_date:
            currency_rates += self.get_rate(date=start_date, api_url=api_url)
            start_date += delta

        sorted_currency_rates = sorted(currency_rates, key=lambda x: x['date'])
        # print(sorted_currency_rates)

        return sorted_currency_rates, provider_id

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
        cu_rates, provider_id = objects
        for cu_rate in cu_rates:
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
                provider_id=provider_id
            )
            check_rate.save()
            currency_rates.append(model_to_dict(check_rate))

        return currency_rates
