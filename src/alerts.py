import os
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
    import json
    creds_dict = None
    if GOOGLE_SHEETS_CREDENTIALS:
        creds_dict = json.loads(GOOGLE_SHEETS_CREDENTIALS)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client

async def send_telegram_alert(alert):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    text = f"{alert['message']}\nTime: {alert['time']}"
    params = {'chat_id': TELEGRAM_CHAT_ID, 'text': text}
    async with aiohttp.ClientSession() as session:
        await session.get(url, params=params)

async def log_to_google_sheet(alert):
    try:
        client = get_google_client()
        sheet = client.open_by_key(GOOGLE_SHEETS_ID).sheet1
        sheet.append_row([alert['time'], alert['symbol'], alert['entry_price'], alert['message']])
    except Exception as e:
        print(f"Google Sheets log error: {e}")
