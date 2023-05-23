from django.shortcuts import render
from currency.services import PrivatExchangeRatesService
from currency.services import ProvidersService


# Create your views here.
def index(request):

    providers = [
        {
            "name": "Privat Bank",
            "api_url": "https://api.privatbank.ua/p24api/exchange_rates"
        }
    ]

    for p in providers:
        provider = ProvidersService()
        provider.create_provider(p)

    service = PrivatExchangeRatesService()
    objects = service.get_rates()
    service.persist_currency_rates(objects)
    return render(request, "core/index.html")
