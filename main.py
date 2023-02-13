import asyncio
import datetime
import platform
import sys

import aiohttp

URL = 'https://api.privatbank.ua/p24api/exchange_rates?date='


def get_day(offset: int):
    return (datetime.datetime.today() + datetime.timedelta(days=-offset)).strftime("%d.%m.%Y")


def get_url(addition: str):
    return URL + addition


async def main(day_cnt):
    exchange_result = []
    if day_cnt > 10:
        day_cnt = 10
    async with aiohttp.ClientSession() as session:
        for day_n in range(day_cnt):
            day_str = get_day(day_n)
            res = dict()
            try:
                async with session.get(get_url(day_str)) as response:
                    if response.status == 200:
                        day_dict = dict()
                        result = await response.json()
                        exchange = list(filter(lambda el: el['currency'] in ('EUR', 'USD'), result['exchangeRate']))
                        for i in exchange:
                            day_dict[i['currency']] = dict()
                            day_dict[i['currency']]['buy'] = i['purchaseRate']
                            day_dict[i['currency']]['sale'] = i['saleRate']
                        res[day_str] = day_dict
                        exchange_result.append(res)
                    else:
                        print(f"Error status: {response.status} for {get_url(day_str)}")
            except aiohttp.ClientConnectorError as err:
                print(f'Connection error: {get_url(day_str)}', str(err))
    return exchange_result


if __name__ == "__main__":
    days_cnt = 1
    if len(sys.argv) > 1:
        days_cnt = int(sys.argv[1])
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main(days_cnt))
    print(r)
