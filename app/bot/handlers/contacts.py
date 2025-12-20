"""
Обработчики для работы с контактами
"""
from telegram import Update
from telegram.ext import ContextTypes
from app.bot.api_client import APIClient
from app.bot.keyboards import get_list_keyboard


async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список контактов"""
    api_client: APIClient = context.user_data.get("api_client")
    
    if not api_client or not api_client.token:
        await update.message.reply_text(
            "❌ Ты не авторизован. Используй /start для авторизации."
        )
        return
    
    try:
        data = await api_client.get_contacts(skip=0, limit=10)
        contacts = data.get("items", [])
        total = data.get("total", 0)
        pages = data.get("pages", 1)
        
        if not contacts:
            await update.message.reply_text("📭 Контактов не найдено.")
            return
        
        # Формируем сообщение
        message = f"👤 <b>Контакты</b> (всего: {total})\n\n"
        for idx, contact in enumerate(contacts[:10], 1):
            first_name = contact.get("first_name", "")
            last_name = contact.get("last_name", "")
            name = f"{first_name} {last_name}".strip() or "Без имени"
            email = contact.get("email", "")
            message += f"{idx}. <b>{name}</b>"
            if email:
                message += f" ({email})"
            message += "\n"
        
        # Клавиатура
        keyboard = get_list_keyboard(contacts, 1, pages, "contact")
        
        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка при получении контактов: {str(e)}"
        )


async def handle_contact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback для контактов"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    api_client: APIClient = context.user_data.get("api_client")
    
    if not api_client or not api_client.token:
        await query.edit_message_text(
            "❌ Ты не авторизован. Используй /start для авторизации."
        )
        return
    
    if data.startswith("contact_item_"):
        # Показать детали контакта
        contact_id = int(data.split("_")[-1])
        try:
            contact = await api_client.get_contact(contact_id)
            
            first_name = contact.get("first_name", "")
            last_name = contact.get("last_name", "")
            name = f"{first_name} {last_name}".strip() or "Без имени"
            
            message = f"👤 <b>{name}</b>\n\n"
            if contact.get("email"):
                message += f"Email: {contact['email']}\n"
            if contact.get("phone"):
                message += f"Телефон: {contact['phone']}\n"
            if contact.get("job_title"):
                message += f"Должность: {contact['job_title']}\n"
            if contact.get("company_id"):
                message += f"Компания ID: {contact['company_id']}\n"
            if contact.get("status"):
                message += f"Статус: {contact['status']}\n"
            if contact.get("notes"):
                message += f"\nЗаметки: {contact['notes'][:200]}...\n"
            
            message += f"\nID: {contact['id']}"
            
            await query.edit_message_text(
                message,
                parse_mode="HTML"
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ Ошибка при получении контакта: {str(e)}"
            )
    
    elif data.startswith("contact_page_"):
        # Пагинация
        page = int(data.split("_")[-1])
        try:
            data = await api_client.get_contacts(skip=(page - 1) * 10, limit=10)
            contacts = data.get("items", [])
            total = data.get("total", 0)
            pages = data.get("pages", 1)
            
            if not contacts:
                await query.edit_message_text("📭 Контактов не найдено.")
                return
            
            message = f"👤 <b>Контакты</b> (всего: {total})\n\n"
            for idx, contact in enumerate(contacts[:10], 1):
                first_name = contact.get("first_name", "")
                last_name = contact.get("last_name", "")
                name = f"{first_name} {last_name}".strip() or "Без имени"
                email = contact.get("email", "")
                message += f"{idx}. <b>{name}</b>"
                if email:
                    message += f" ({email})"
                message += "\n"
            
            keyboard = get_list_keyboard(contacts, page, pages, "contact")
            await query.edit_message_text(
                message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ Ошибка: {str(e)}"
            )
    
    elif data == "contact_back":
        # Вернуться к списку
        await show_contacts(update, context)

