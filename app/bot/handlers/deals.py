"""
Обработчики для работы со сделками
"""
from telegram import Update
from telegram.ext import ContextTypes
from app.bot.api_client import APIClient
from app.bot.keyboards import get_list_keyboard, get_deal_status_keyboard


async def show_deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список сделок"""
    api_client: APIClient = context.user_data.get("api_client")
    
    if not api_client or not api_client.token:
        await update.message.reply_text(
            "❌ Ты не авторизован. Используй /start для авторизации."
        )
        return
    
    try:
        data = await api_client.get_deals(skip=0, limit=10)
        deals = data.get("items", [])
        total = data.get("total", 0)
        pages = data.get("pages", 1)
        
        if not deals:
            await update.message.reply_text("📭 Сделок не найдено.")
            return
        
        # Формируем сообщение
        message = f"💼 <b>Сделки</b> (всего: {total})\n\n"
        for idx, deal in enumerate(deals[:10], 1):
            title = deal.get("title", "Без названия")
            status = deal.get("status", "N/A")
            amount = deal.get("amount")
            amount_str = f" - {amount} {deal.get('currency', 'RUB')}" if amount else ""
            message += f"{idx}. <b>{title}</b> [{status}]{amount_str}\n"
        
        # Клавиатура
        keyboard = get_list_keyboard(deals, 1, pages, "deal")
        
        await update.message.reply_text(
            message,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка при получении сделок: {str(e)}"
        )


async def handle_deal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback для сделок"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    api_client: APIClient = context.user_data.get("api_client")
    
    if not api_client or not api_client.token:
        await query.edit_message_text(
            "❌ Ты не авторизован. Используй /start для авторизации."
        )
        return
    
    if data.startswith("deal_item_"):
        # Показать детали сделки
        deal_id = int(data.split("_")[-1])
        try:
            deal = await api_client.get_deal(deal_id)
            
            message = f"💼 <b>{deal.get('title', 'Без названия')}</b>\n\n"
            if deal.get("description"):
                message += f"Описание: {deal['description'][:200]}...\n\n"
            if deal.get("amount"):
                message += f"Сумма: {deal['amount']} {deal.get('currency', 'RUB')}\n"
            if deal.get("probability") is not None:
                message += f"Вероятность: {deal['probability']}%\n"
            if deal.get("status"):
                message += f"Статус: {deal['status']}\n"
            if deal.get("expected_close_date"):
                message += f"Ожидаемая дата закрытия: {deal['expected_close_date']}\n"
            if deal.get("contact_id"):
                message += f"Контакт ID: {deal['contact_id']}\n"
            if deal.get("company_id"):
                message += f"Компания ID: {deal['company_id']}\n"
            
            message += f"\nID: {deal['id']}"
            
            # Клавиатура для изменения статуса
            keyboard = get_deal_status_keyboard(deal_id)
            
            await query.edit_message_text(
                message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ Ошибка при получении сделки: {str(e)}"
            )
    
    elif data.startswith("deal_detail_"):
        # Вернуться к деталям сделки
        deal_id = int(data.split("_")[-1])
        try:
            deal = await api_client.get_deal(deal_id)
            
            message = f"💼 <b>{deal.get('title', 'Без названия')}</b>\n\n"
            if deal.get("description"):
                message += f"Описание: {deal['description'][:200]}...\n\n"
            if deal.get("amount"):
                message += f"Сумма: {deal['amount']} {deal.get('currency', 'RUB')}\n"
            if deal.get("probability") is not None:
                message += f"Вероятность: {deal['probability']}%\n"
            if deal.get("status"):
                message += f"Статус: {deal['status']}\n"
            
            keyboard = get_deal_status_keyboard(deal_id)
            await query.edit_message_text(
                message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ Ошибка: {str(e)}"
            )
    
    elif data.startswith("deal_status_"):
        # Изменение статуса сделки
        # Формат: deal_status_{deal_id}|{status}
        try:
            parts = data.split("|", 1)
            if len(parts) == 2:
                deal_id_part = parts[0].replace("deal_status_", "")
                deal_id = int(deal_id_part)
                status = parts[1]  # Статус может содержать пробелы
                
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.put(
                        f"{api_client.base_url}/deals/{deal_id}/status",
                        json={"status": status},
                        headers=api_client._get_headers()
                    )
                    response.raise_for_status()
                    deal = response.json()
                
                await query.edit_message_text(
                    f"✅ Статус сделки изменен на: <b>{status}</b>",
                    parse_mode="HTML"
                )
                
                # Показываем обновленные детали через небольшую задержку
                import asyncio
                await asyncio.sleep(0.5)
                # Создаем новый callback для показа деталей
                query.data = f"deal_item_{deal_id}"
                await handle_deal_callback(update, context)
            else:
                await query.edit_message_text("❌ Неверный формат запроса")
        except Exception as e:
            await query.edit_message_text(
                f"❌ Ошибка при изменении статуса: {str(e)}"
            )
    
    elif data.startswith("deal_page_"):
        # Пагинация
        page = int(data.split("_")[-1])
        try:
            data = await api_client.get_deals(skip=(page - 1) * 10, limit=10)
            deals = data.get("items", [])
            total = data.get("total", 0)
            pages = data.get("pages", 1)
            
            if not deals:
                await query.edit_message_text("📭 Сделок не найдено.")
                return
            
            message = f"💼 <b>Сделки</b> (всего: {total})\n\n"
            for idx, deal in enumerate(deals[:10], 1):
                title = deal.get("title", "Без названия")
                status = deal.get("status", "N/A")
                amount = deal.get("amount")
                amount_str = f" - {amount} {deal.get('currency', 'RUB')}" if amount else ""
                message += f"{idx}. <b>{title}</b> [{status}]{amount_str}\n"
            
            keyboard = get_list_keyboard(deals, page, pages, "deal")
            await query.edit_message_text(
                message,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ Ошибка: {str(e)}"
            )
    
    elif data == "deal_back":
        # Вернуться к списку
        await show_deals(update, context)

