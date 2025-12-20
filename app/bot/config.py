"""
Конфигурация Telegram бота
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()


class BotSettings:
    """Настройки Telegram бота"""
    
    def __init__(self):
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        
        self.API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


bot_settings = BotSettings()

