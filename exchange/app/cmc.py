import requests

class CoinMarketCup:
    def __init__(self):
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

        self.params = {
            "start": "1",
            "limit": "1",
            "convert": "USD"
        }

        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '65d77960-ee00-4fe5-8a87-88354c79a4a1',
        }

    def updated_data(self):
        r = requests.get (url=self.url, headers=self.headers, params=self.params).json()
        BTCPrice = r['data'][0]['quote']['USD']['price']
        return BTCPrice
