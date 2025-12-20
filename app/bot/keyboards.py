"""
Клавиатуры для Telegram бота
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional, Dict


def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    keyboard = [
        [KeyboardButton("🏢 Компании"), KeyboardButton("👤 Контакты")],
        [KeyboardButton("💼 Сделки"), KeyboardButton("🔐 Выйти")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    prefix: str,
    item_id: Optional[int] = None
) -> InlineKeyboardMarkup:
    """Клавиатура для пагинации"""
    buttons = []
    
    # Кнопки навигации
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton("◀️ Назад", callback_data=f"{prefix}_page_{current_page - 1}")
        )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton("Вперед ▶️", callback_data=f"{prefix}_page_{current_page + 1}")
        )
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    # Кнопка деталей (если передан item_id)
    if item_id:
        buttons.append([
            InlineKeyboardButton("📋 Детали", callback_data=f"{prefix}_detail_{item_id}")
        ])
    
    buttons.append([
        InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(buttons)


def get_list_keyboard(
    items: List[Dict],
    current_page: int,
    total_pages: int,
    prefix: str,
    limit: int = 10
) -> InlineKeyboardMarkup:
    """Клавиатура для списка элементов с пагинацией"""
    buttons = []
    
    # Кнопки элементов (первые 5)
    start_idx = (current_page - 1) * limit
    for idx, item in enumerate(items[:5], start=start_idx):
        name = item.get("name") or item.get("title") or f"#{item.get('id')}"
        buttons.append([
            InlineKeyboardButton(
                f"{idx + 1}. {name[:30]}",
                callback_data=f"{prefix}_item_{item['id']}"
            )
        ])
    
    # Навигация
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton("◀️", callback_data=f"{prefix}_page_{current_page - 1}")
        )
    nav_buttons.append(
        InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop")
    )
    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton("▶️", callback_data=f"{prefix}_page_{current_page + 1}")
        )
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([
        InlineKeyboardButton("🔙 Назад", callback_data=f"{prefix}_back")
    ])
    
    return InlineKeyboardMarkup(buttons)


def get_deal_status_keyboard(deal_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для изменения статуса сделки"""
    # Используем | как разделитель, чтобы избежать проблем с пробелами
    buttons = [
        [
            InlineKeyboardButton("🆕 Новая", callback_data=f"deal_status_{deal_id}|Новая"),
            InlineKeyboardButton("⚙️ В работе", callback_data=f"deal_status_{deal_id}|В работе")
        ],
        [
            InlineKeyboardButton("✅ Завершена", callback_data=f"deal_status_{deal_id}|Завершена"),
            InlineKeyboardButton("❌ Отменена", callback_data=f"deal_status_{deal_id}|Отменена")
        ],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"deal_detail_{deal_id}")]
    ]
    return InlineKeyboardMarkup(buttons)

