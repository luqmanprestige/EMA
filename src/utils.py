import aiohttp

async def get_all_usdt_pairs():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            symbols = [
                s['symbol']
                for s in data['symbols']
                if (
                    s['quoteAsset'] == 'USDT' and
                    s['status'] == 'TRADING' and
                    s['isSpotTradingAllowed'] == True
                )
            ]
            return symbols
