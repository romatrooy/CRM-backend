"""
Главный файл Telegram бота
"""
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)

from app.bot.config import bot_settings
from app.bot.handlers.auth import (
    start,
    handle_email,
    handle_password,
    logout,
    cancel,
    WAITING_EMAIL,
    WAITING_PASSWORD
)
from app.bot.handlers.companies import show_companies, handle_company_callback
from app.bot.handlers.contacts import show_contacts, handle_contact_callback
from app.bot.handlers.deals import show_deals, handle_deal_callback
from app.bot.keyboards import get_main_menu

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def setup_handlers(application: Application):
    """Настройка обработчиков"""
    
    # ConversationHandler для авторизации
    auth_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email)],
            WAITING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Обработчики команд
    application.add_handler(auth_handler)
    application.add_handler(CommandHandler("logout", logout))
    
    # Обработчики кнопок главного меню
    application.add_handler(MessageHandler(filters.Regex("^🏢 Компании$"), show_companies))
    application.add_handler(MessageHandler(filters.Regex("^👤 Контакты$"), show_contacts))
    application.add_handler(MessageHandler(filters.Regex("^💼 Сделки$"), show_deals))
    application.add_handler(MessageHandler(filters.Regex("^🔐 Выйти$"), logout))
    
    # Обработчики callback для компаний
    application.add_handler(CallbackQueryHandler(handle_company_callback, pattern="^company_"))
    
    # Обработчики callback для контактов
    application.add_handler(CallbackQueryHandler(handle_contact_callback, pattern="^contact_"))
    
    # Обработчики callback для сделок
    application.add_handler(CallbackQueryHandler(handle_deal_callback, pattern="^deal_"))
    
    # Обработчик главного меню и noop
    application.add_handler(CallbackQueryHandler(
        lambda u, c: u.callback_query.answer("Используй кнопки меню"),
        pattern="^main_menu$"
    ))
    application.add_handler(CallbackQueryHandler(
        lambda u, c: u.callback_query.answer(),  # Просто отвечаем на callback
        pattern="^noop$"
    ))


def main():
    """Запуск бота"""
    # Создание приложения
    application = Application.builder().token(bot_settings.TELEGRAM_BOT_TOKEN).build()
    
    # Настройка обработчиков
    setup_handlers(application)
    
    # Запуск бота
    logger.info("Бот запущен")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

