from decimal import Decimal
import json
import urllib.request

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def get_price(request):
    print(request.body)
    symbol = json.loads(request.body).get("result").get("parameters").get("symbol")
    stock_info = json.loads(urllib.request.urlopen(
        "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&"
        "symbol={}&interval=1min&apikey=AHY5RTTYJ34OILWU".format(symbol)).read())
    latest_info = sorted([(time, values) 
        for time, values in stock_info.get("Time Series (1min)").items()])[-1]
    price = Decimal(latest_info[1].get("4. close"))

    speech = "The price at {} is {}".format(latest_info[0], price)

    print(speech)

    return JsonResponse({
        "speech": speech,
        "displayText": speech,
        "source": "robin-cat",
    })
