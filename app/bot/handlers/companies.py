"""
Обработчики для работы с компаниями
"""
from telegram import Update
from telegram.ext import ContextTypes
from app.bot.api_client import APIClient
from app.bot.keyboards import get_list_keyboard, get_pagination_keyboard


async def show_companies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список компаний"""
    api_client: APIClient = context.user_data.get("api_client")
    
    if not api_client or not api_client.token:
        await update.message.reply_text(
            "❌ Ты не авторизован. Используй /start для авторизации."
        )
        return
    
    try:
        data = await api_client.get_companies(skip=0, limit=10)
        companies = data.get("items", [])
        total = data.get("total", 0)
        pages = data.get("pages", 1)
        
        if not companies:
            await update.message.reply_text("📭 Компаний не найдено.")
            return
        
        # Формируем сообщение
        message = f"🏢 <b>Компании</b> (всего: {total})\n\n"
        for idx, company in enumerate(companies[:10], 1):
            name = company.get("name", "Без названия")
            status = company.get("status", "N/A")
            message += f"{idx}. <b>{name}</b> [{status}]\n"
        
        # Клавиатура
        keyboard = get_list_keyboard(companies, 1, pages, "company")
        
        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка при получении компаний: {str(e)}"
        )


async def handle_company_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback для компаний"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    api_client: APIClient = context.user_data.get("api_client")
    
    if not api_client or not api_client.token:
        await query.edit_message_text(
            "❌ Ты не авторизован. Используй /start для авторизации."
        )
        return
    
    if data.startswith("company_item_"):
        # Показать детали компании
        company_id = int(data.split("_")[-1])
        try:
            company = await api_client.get_company(company_id)
            
            message = f"🏢 <b>{company.get('name', 'Без названия')}</b>\n\n"
            if company.get("legal_name"):
                message += f"Юридическое название: {company['legal_name']}\n"
            if company.get("email"):
                message += f"Email: {company['email']}\n"
            if company.get("phone"):
                message += f"Телефон: {company['phone']}\n"
            if company.get("website"):
                message += f"Сайт: {company['website']}\n"
            if company.get("industry"):
                message += f"Отрасль: {company['industry']}\n"
            if company.get("status"):
                message += f"Статус: {company['status']}\n"
            if company.get("description"):
                message += f"\nОписание: {company['description'][:200]}...\n"
            
            message += f"\nID: {company['id']}"
            
            await query.edit_message_text(
                message,
                parse_mode="HTML"
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ Ошибка при получении компании: {str(e)}"
            )
    
    elif data.startswith("company_page_"):
        # Пагинация
        page = int(data.split("_")[-1])
        try:
            data = await api_client.get_companies(skip=(page - 1) * 10, limit=10)
            companies = data.get("items", [])
            total = data.get("total", 0)
            pages = data.get("pages", 1)
            
            if not companies:
                await query.edit_message_text("📭 Компаний не найдено.")
                return
            
            message = f"🏢 <b>Компании</b> (всего: {total})\n\n"
            for idx, company in enumerate(companies[:10], 1):
                name = company.get("name", "Без названия")
                status = company.get("status", "N/A")
                message += f"{idx}. <b>{name}</b> [{status}]\n"
            
            keyboard = get_list_keyboard(companies, page, pages, "company")
            await query.edit_message_text(
                message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ Ошибка: {str(e)}"
            )
    
    elif data == "company_back":
        # Вернуться к списку
        await show_companies(update, context)

