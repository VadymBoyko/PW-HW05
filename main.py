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


def get_day_exchange(day_params):
    return day_params['currency'], day_params['purchaseRate'], day_params['saleRate']


def process_day_exchange(day_str, param):
    result = dict()
    day_dict = dict()
    exchange = list(filter(lambda el: el['currency'] in ('EUR', 'USD'), param['exchangeRate']))
    for i in exchange:
        cur_name, cur_buy, cur_sale = get_day_exchange(i)
        day_dict[cur_name] = dict()
        day_dict[cur_name]['buy'] = cur_buy
        day_dict[cur_name]['sale'] = cur_sale
    result[day_str] = day_dict
    return result


async def main(day_cnt):
    exchange_result = []
    if day_cnt > 10:
        day_cnt = 10
    async with aiohttp.ClientSession() as session:
        for day_n in range(day_cnt):
            day_str = get_day(day_n)
            try:
                async with session.get(get_url(day_str)) as response:
                    if response.status == 200:
                        exchange_result.append(process_day_exchange(day_str, await response.json()))
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
    r = asyncio.run(main(3))
    print(r)
