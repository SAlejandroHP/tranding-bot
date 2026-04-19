import os
import requests
from dotenv import load_dotenv

class TelegramNotifier:
    def __init__(self):
        load_dotenv()
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def enviar_alerta(self, mensaje):
        if not self.token or not self.chat_id:
            return
            
        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            requests.post(url, data={"chat_id": self.chat_id, "text": mensaje}, timeout=5)
        except Exception as e:
            print(f"Error enviando alerta de Telegram: {e}")
