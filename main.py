import asyncio
import platform
import sys
from datetime import datetime, timedelta

import aiohttp


def urls_producer(days):
    urls = []
    today = datetime.now()
    for i in range(0, days + 1):
        days_before = timedelta(i)
        date = (today - days_before).strftime('%d.%m.%Y')
        urls.append(f"https://api.privatbank.ua/p24api/exchange_rates?date={date}")
    return urls


def verification_input():
    data = sys.argv[-1]
    if data.isdigit():
        if int(data) <= 10:
            days = int(data)
        else:
            print("Wrong arguments. The exchange rate will be shown for today. Try number between 0 and 10.")
            days = 0
    else:
        print("Wrong arguments. The exchange rate will be shown for today. Try number between 0 and 10.")
        days = 0
    return days


async def main():
    async with aiohttp.ClientSession() as session:
        print("|{:^15}|{:^15}|{:^15}|{:^15}|".format("Date", "Currency", "Sale, UAH", "Buy, UAH"))
        for url in urls:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        res = await response.json()
                        for i in res['exchangeRate']:
                            if i['currency'] == 'USD':
                                print("|{:^15}|{:^15}|{:^15}|{:^15}|".format(res['date'], i['currency'], i['saleRate'], i['purchaseRate']))
                            elif i['currency'] == 'EUR':
                                print("|{:^15}|{:^15}|{:^15}|{:^15}|".format(res['date'], i['currency'], i['saleRate'], i['purchaseRate']))
                    else:
                        print(f"Error status: {response.status} for {url}")
            except aiohttp.ClientConnectorError as err:
                print(f'Connection error: {url}', str(err))


if __name__ == "__main__":

    input_data = verification_input()
    urls = urls_producer(input_data)

    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main())
