import asyncio
import logging
from datetime import datetime, timedelta

import aiohttp
import names
import websockets
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)


def data_parser(data: str):
    commands = data.split(' ')
    return commands


def verification_input(data):
    data = data
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


async def request(currency, urls):
    async with aiohttp.ClientSession() as session:
        result = []
        for url in urls:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        res = await response.json()
                        for i in res['exchangeRate']:
                            if i['currency'] == currency:
                                result.append(
                                    f"Date: {res['date']} | Currency: {i['currency']} | Sale: {i['saleRate']} UAH | "
                                    f"Buy: {i['purchaseRate']} UAH |")
                    else:
                        print(f"Error status: {response.status} for {url}")
            except aiohttp.ClientConnectorError as err:
                print(f'Connection error: {url}', str(err))
        return result


def urls_producer(days):
    urls = []
    today = datetime.now()
    for i in range(0, days + 1):
        days_before = timedelta(i)
        date = (today - days_before).strftime('%d.%m.%Y')
        urls.append(f"https://api.privatbank.ua/p24api/exchange_rates?date={date}")
    return urls


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def send_to_client(self, message: str, ws: WebSocketServerProtocol):
        await ws.send(message)

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            msg = data_parser(message)
            if msg[0] == "exc" and len(msg) == 3:
                data = msg[2]
                if data.isdigit():
                    if int(data) <= 10:
                        days = int(data)
                    else:
                        await self.send_to_client("Wrong arguments. The exchange rate will be shown for today. Try "
                                                  "number between 0 and 10.", ws)
                        days = 0
                else:
                    await self.send_to_client("Wrong arguments. The exchange rate will be shown for today. Try number "
                                              "between 0 and 10.", ws)
                    days = 0

                urls = urls_producer(days)
                currency = msg[1]
                exchange_rate = await request(currency, urls)
                for i in exchange_rate:
                    await self.send_to_client(i, ws)
            elif msg[0] == "exc" and len(msg) == 2:
                days = 0
                urls = urls_producer(days)
                currency = msg[1]
                exchange_rate = await request(currency, urls)
                for i in exchange_rate:
                    await self.send_to_client(i, ws)
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    asyncio.run(main())
