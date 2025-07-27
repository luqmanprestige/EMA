import aiohttp

BINANCE_API = 'https://api.binance.com/api/v3/ticker/price'

async def get_all_usdt_pairs():
    async with aiohttp.ClientSession() as session:
        async with session.get(BINANCE_API) as resp:
            data = await resp.json()
            symbols = [item['symbol'] for item in data if item['symbol'].endswith('USDT')]
            return symbols
