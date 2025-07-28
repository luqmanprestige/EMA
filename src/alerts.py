import os
import json
import aiohttp
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GOOGLE_SHEETS_ID = os.getenv('GOOGLE_SHEETS_ID')
GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS')

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

def get_google_client():
    try:
        if not GOOGLE_SHEETS_CREDENTIALS:
            raise ValueError("Missing Google Sheets credentials.")
        creds_dict = json.loads(GOOGLE_SHEETS_CREDENTIALS)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"[ERROR] Google Client Init Failed: {e}")
        return None

async def send_telegram_alert(alert):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] Telegram credentials missing.")
        return

    if not alert.get('message') or not alert.get('time'):
        print(f"[ERROR] Invalid alert format: {alert}")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    text = f"{alert['message']}\nTime: {alert['time']}"

    params = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text
    }

    # Filter out None values
    params = {k: v for k, v in params.items() if v is not None}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    err_text = await resp.text()
                    print(f"[ERROR] Telegram API failed: {resp.status} - {err_text}")
        except Exception as e:
            print(f"[ERROR] Telegram request failed: {e}")

async def log_to_google_sheet(alert):
    try:
        if not all(key in alert for key in ['time', 'symbol', 'entry_price', 'message']):
            print(f"[ERROR] Incomplete alert for logging: {alert}")
            return

        client = get_google_client()
        if not client:
            return
        sheet = client.open_by_key(GOOGLE_SHEETS_ID).sheet1
        sheet.append_row([
            alert['time'],
            alert['symbol'],
            alert['entry_price'],
            alert['message']
        ])
    except Exception as e:
        print(f"[ERROR] Google Sheets log failed: {e}")
