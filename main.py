import asyncio
from datetime import datetime, timezone, timedelta
from src.binance_scanner import scan_binance_pairs
from src.alerts import send_telegram_alert, log_to_google_sheet
from src.state_manager import load_state, save_state
from src.utils import get_all_usdt_pairs

SCAN_INTERVAL = 60  # seconds
utc_plus_4 = timezone(timedelta(hours=4))

async def main_loop():
    print("Starting Binance Pump Bot...")
    state = load_state()
    symbols = await get_all_usdt_pairs()

    while True:
        current_time = datetime.now(utc_plus_4).strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n[INFO] Scanning at {current_time} UTC+4")
        alerts = await scan_binance_pairs(symbols, state)

        for alert in alerts:
            await send_telegram_alert(alert)
            await log_to_google_sheet(alert)
            state[alert['symbol']] = alert['entry_price']
            save_state(state)

        await asyncio.sleep(SCAN_INTERVAL)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("Bot stopped.")
