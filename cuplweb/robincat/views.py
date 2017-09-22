from decimal import Decimal
import json
import urllib.request

from django.http import JsonResponse


def get_price(request):
	try:
		symbol = request.POST.get("result").get("parameters").get("symbol")
	except Exception:
		return 
	stock_info = json.loads(urllib.request.urlopen(
		f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&"
		f"symbol={symbol}&interval=1min&apikey=AHY5RTTYJ34OILWU").read())
	latest_info = sorted([(time, values) 
		for time, values in stock_info.get("Time Series (1min)").items()])[-1]
	price = Decimal(latest_info[1].get("4. close"))

	speech = f"The price at {latest_info[0]} is {print}"

    print(speech)

    return JsonResponse({
        "speech": speech,
        "displayText": speech,
        "source": "robin-cat",
    })
