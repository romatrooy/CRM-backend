"""
Обработчики авторизации
"""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from app.bot.api_client import APIClient
from app.bot.keyboards import get_main_menu

# Состояния для ConversationHandler
WAITING_EMAIL, WAITING_PASSWORD = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Проверяем, есть ли уже токен
    if "api_client" not in context.user_data:
        context.user_data["api_client"] = APIClient()
    
    api_client: APIClient = context.user_data["api_client"]
    
    if api_client.token:
        await update.message.reply_text(
            f"Привет, {user.first_name}! Ты уже авторизован.\n\n"
            "Используй меню для работы с CRM.",
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            f"Привет, {user.first_name}! 👋\n\n"
            "Для работы с CRM системой нужно авторизоваться.\n\n"
            "Введи свой email:"
        )
        return WAITING_EMAIL


async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик ввода email"""
    email = update.message.text.strip()
    context.user_data["email"] = email
    
    await update.message.reply_text(
        "Теперь введи пароль:"
    )
    return WAITING_PASSWORD


async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик ввода пароля и авторизации"""
    password = update.message.text
    email = context.user_data.get("email")
    
    api_client: APIClient = context.user_data.get("api_client", APIClient())
    
    try:
        response = await api_client.login(email, password)
        token = response.get("access_token")
        
        if token:
            api_client.set_token(token)
            context.user_data["api_client"] = api_client
            await update.message.reply_text(
                "✅ Авторизация успешна!\n\n"
                "Теперь ты можешь работать с CRM системой.",
                reply_markup=get_main_menu()
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                "❌ Ошибка авторизации. Попробуй снова.\n\n"
                "Введи email:"
            )
            return WAITING_EMAIL
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Неверный" in error_msg:
            await update.message.reply_text(
                "❌ Неверный email или пароль.\n\n"
                "Попробуй снова. Введи email:"
            )
        else:
            await update.message.reply_text(
                f"❌ Ошибка при авторизации: {error_msg}\n\n"
                "Попробуй снова. Введи email:"
            )
        return WAITING_EMAIL


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выхода из системы"""
    if "api_client" in context.user_data:
        api_client: APIClient = context.user_data["api_client"]
        api_client.clear_token()
    
    context.user_data.clear()
    
    await update.message.reply_text(
        "👋 Ты вышел из системы.\n\n"
        "Для повторной авторизации используй /start"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена авторизации"""
    await update.message.reply_text(
        "Авторизация отменена. Используй /start для начала."
    )
    return ConversationHandler.END

