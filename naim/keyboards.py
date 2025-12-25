"""Модуль с функциями для создания клавиатур бота"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def buttons_start_02():
    """Создает кнопки стартового меню"""
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="🛒 Сделать заказ",
                                callback_data="make_order")

    btn2 = InlineKeyboardButton(text="❓FAQ",
                                callback_data="faq")
    btn3 = InlineKeyboardButton(text="📍Контакты ",
                                callback_data="contacts")

    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn3)

    return menu

