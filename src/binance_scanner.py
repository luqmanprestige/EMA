import aiohttp
import pandas as pd
import numpy as np
from ta.trend import EMAIndicator
from datetime import datetime

BINANCE_API = 'https://api.binance.com/api/v3/klines'

async def fetch_klines(session, symbol, interval, limit=100):
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    async with session.get(BINANCE_API, params=params) as resp:
        data = await resp.json()
        return data

def calculate_emas(df):
    df['close'] = pd.to_numeric(df['close'])
    df['volume'] = pd.to_numeric(df['volume'])
    df['EMA7'] = EMAIndicator(df['close'], window=7).ema_indicator()
    df['EMA25'] = EMAIndicator(df['close'], window=25).ema_indicator()
    df['EMA50'] = EMAIndicator(df['close'], window=50).ema_indicator()
    df['EMA99'] = EMAIndicator(df['close'], window=99).ema_indicator()
    return df

def check_volume_spike(df):
    avg_vol = df['volume'].rolling(window=20).mean().iloc[-2]
    last_vol = df['volume'].iloc[-1]
    return last_vol > 2.5 * avg_vol

def price_change_last_15m(df):
    last_close = df['close'].iloc[-1]
    prev_close = df['close'].iloc[-2]
    pct_change = (last_close - prev_close) / prev_close * 100
    return pct_change

async def scan_binance_pairs(symbols, state):
    alerts = []
    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            try:
                klines_15m = await fetch_klines(session, symbol, '15m')
                df_15m = pd.DataFrame(klines_15m, columns=[
                    'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                    'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                    'taker_buy_quote_asset_volume', 'ignore'])
                df_15m['close'] = df_15m['close'].astype(float)
                df_15m['volume'] = df_15m['volume'].astype(float)

                df_15m = calculate_emas(df_15m)

                ema25 = df_15m['EMA25'].iloc[-1]
                ema99 = df_15m['EMA99'].iloc[-1]
                ema7 = df_15m['EMA7'].iloc[-1]

                prev_ema25 = df_15m['EMA25'].iloc[-2]
                prev_ema99 = df_15m['EMA99'].iloc[-2]

                crossover = prev_ema25 < prev_ema99 and ema25 > ema99
                alignment = ema7 > ema25 > ema99
                volume_spike = check_volume_spike(df_15m)
                price_change = price_change_last_15m(df_15m)

                if crossover and alignment and volume_spike and price_change < 5:
                    if symbol not in state:  # Avoid duplicate alerts
                        alert = {
                            'symbol': symbol,
                            'entry_price': df_15m['close'].iloc[-1],
                            'time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                            'message': f"🚀 Pump detected on {symbol} at price {df_15m['close'].iloc[-1]:.5f}"
                        }
                        alerts.append(alert)
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
    return alerts
