from django.shortcuts import render
from currency.services import PrivatExchangeRatesService
from currency.services import ProvidersService


# Create your views here.
def index(request):

    bank = {
        "name": "Privat Bank",
        "api_url": "https://api.privatbank.ua/p24api/exchange_rates"
    }

    provider_service = ProvidersService(name=bank.get('name'), api_url=bank.get('api_url'))
    provider = provider_service.get_or_create()

    # Создание объекта ExchangeRatesService с передачей provider в конструктор
    exchange_service = PrivatExchangeRatesService(provider=provider)

    objects = exchange_service.get_rates()
    print(objects)
    # exchange_service.persist_currency_rates(objects)

    return render(request, "core/index.html")
