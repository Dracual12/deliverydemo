from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.deep_linking import decode_payload
from config import dp, bot, db
from datetime import datetime
from waiters import waiter_start as w_start
from naim.main import buttons_start_02
import time
import sys
import os

from files.icons import icons




def create_menu_buttons_with_back():
    """Создает кнопки категорий меню с кнопкой возврата в главное меню"""
    menu = InlineKeyboardMarkup()
    for e in db.get_all_categories():
        menu.add(InlineKeyboardButton(text=f"{e} {icons[e]}",
                                      callback_data=f"category_menu_{e}"))
    back_btn = InlineKeyboardButton(text="⬅️ Назад",
                                    callback_data="back_to_start")
    menu.add(back_btn)
    return menu


# Регистрируем обработчики кнопок стартового меню с использованием text= для точного совпадения
# Важно: эти обработчики должны быть зарегистрированы ДО общих обработчиков с text_contains
@dp.callback_query_handler(text="make_order")
async def make_order_handler(call: types.CallbackQuery):
    """Обработчик кнопки 'Сделать заказ' - сразу показывает категории меню"""
    await call.answer()
    user = call.from_user.id
    print(f"Make order handler called, callback_data: {call.data}")
    text = 'Выбери категорию меню 🔍'
    try:
        await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=text,
            reply_markup=create_menu_buttons_with_back()
        )
    except Exception as e:
        print(f"Error in make_order_handler: {e}")
        await bot.send_message(chat_id=user, text=text, reply_markup=create_menu_buttons_with_back())


@dp.callback_query_handler(text="faq")
async def faq_handler(call: types.CallbackQuery):
    """Обработчик кнопки FAQ"""
    await call.answer()
    user = call.from_user.id
    print(f"FAQ handler called, callback_data: {call.data}")
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    btn1 = InlineKeyboardButton(text="Можно ли заказать еду навынос?",
                                callback_data="faq_takeaway")
    btn2 = InlineKeyboardButton(text="Как узнать информацию о пищевой ценности блюд?",
                                callback_data="faq_nutrition")
    btn3 = InlineKeyboardButton(text="Как оформить доставку?",
                                callback_data="faq_delivery")
    btn_back = InlineKeyboardButton(text="⬅️ Назад",
                                    callback_data="back_to_start")
    
    keyboard.add(btn1, btn2, btn3, btn_back)
    
    await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text="❓ <b>Часто задаваемые вопросы</b>\n\nВыберите вопрос:",
        reply_markup=keyboard,
        parse_mode='HTML'
    )


@dp.callback_query_handler(text_contains="faq_")
async def faq_answer_handler(call: types.CallbackQuery):
    """Обработчик ответов на вопросы FAQ"""
    await call.answer()
    user = call.from_user.id
    faq_type = call.data.split("_")[-1]
    
    answers = {
        "takeaway": "Да, передайте заказ официанту, уточнив, что он будет навынос, и мы соберём блюда для вас с собой! ☺️",
        "nutrition": "В карточке каждой позиции есть кнопки, нажав на которые вы узнаете КБЖУ, а также полный состав блюда! 😌",
        "delivery": "Блюда с доставкой можно заказать в нашем приложении, а также через сервисы Yandex Go и Delivery Club! 😊"
    }
    
    answer = answers.get(faq_type, "Ответ не найден")
    
    keyboard = InlineKeyboardMarkup()
    btn_back = InlineKeyboardButton(text="⬅️ Назад к вопросам",
                                    callback_data="faq")
    keyboard.add(btn_back)
    
    await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=answer,
        reply_markup=keyboard
    )


@dp.callback_query_handler(text="contacts")
async def contacts_handler(call: types.CallbackQuery):
    """Обработчик кнопки Контакты"""
    await call.answer()
    user = call.from_user.id
    print(f"Contacts handler called, callback_data: {call.data}")
    
    contacts_text = (
        "<b>Наши рестораны</b>\n\n"
        "📍 <b>Korean Chick Бауманская</b>\n"
        "м. Бауманская, Посланников пер., д. 18, стр.1\n"
        "10:00–22:00\n"
        "+7 (968) 730-00-30\n\n"
        "📍 <b>Korean Chick Водный Стадион</b>\n"
        "м. Водный стадион, ул. Кронштадтский бульвар, 3с1\n"
        "10:00–22:00\n"
        "+7 (968) 730-00-40\n\n"
        "📍 <b>Korean Chick Выхино</b>\n"
        "м. Выхино / Новогиреево, ул. Вешняковская, д. 12Ж\n"
        "10:00–22:00\n"
        "+7 (968) 730-00-60\n\n"
        "📍 <b>Korean Chick Кунцево</b>\n"
        "м. Кунцевская, ул. Кунцевская, д. 5\n"
        "10:00–22:00\n"
        "+7 (968) 730-00-10\n\n"
        "📍 <b>Korean Chick Пятницкое Шоссе</b>\n"
        "м. Пятницкое шоссе, Ангелов переулок, д. 9\n"
        "10:00–22:00\n"
        "+7 (968) 730-00-80\n\n"
        "📍 <b>Korean Chick Октябрьское Поле</b>\n"
        "м. Октябрьское поле, ул. Маршала Мерецкова, д. 4\n"
        "10:00–22:00\n"
        "+7 (968) 730-00-70\n\n"
        "📍 <b>Korean Chick Измайловский Бульвар</b>\n"
        "ул. Измайловский бульвар, 11/31\n"
        "10:00–22:00\n"
        "+7 (968) 730-00-20\n\n"
        "📍 <b>Korean Chick Раменки</b>\n"
        "м. Раменки, Мичуринский проспект, д. 31к7\n"
        "10:00–22:00\n"
        "+7 (968) 730-00-50\n\n"
        "📍 <b>Korean Chick Красногорск</b>\n"
        "ул. Ленина, д. 26А (ТЦ «Ёлка», 2 этаж)\n"
        "10:00–22:00\n"
        "+7 (968) 730-00-94\n\n"
        "📍 <b>Korean Chick Медведково</b>\n"
        "м. Медведково, ул. Молодцова, д. 4а\n"
        "10:00–22:00\n"
        "+7 (968) 730-00-31\n\n"
        "📍 <b>Korean Chick Суханово</b>\n"
        "Москва, Расторгуевское шоссе, д. 5\n"
        "10:00–22:30\n"
        "Пт–Сб: 10:00–22:45"
    )
    
    keyboard = InlineKeyboardMarkup()
    btn_back = InlineKeyboardButton(text="⬅️ Назад",
                                    callback_data="back_to_start")
    keyboard.add(btn_back)
    
    await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=contacts_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )


@dp.callback_query_handler(text="back_to_start")
async def back_to_start_handler(call: types.CallbackQuery):
    """Обработчик возврата в главное меню"""
    await call.answer()
    user = call.from_user.id
    
    text = ("👋 Добро пожаловать в <b>KoreanChick</b>!\n"
            "Я — виртуальный ассистент нашей сети ресторанов.\n"
            "Здесь можно:\n\n"
            "• 🛒 сделать заказ\n"
            "• ❓ узнать ответы на частые вопросы\n"
            "• 📍 посмотреть адреса и контакты ресторанов\n\n"
            "С чем могу помочь?")
    
    await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=text,
        reply_markup=buttons_start_02(),
        parse_mode='HTML'
    )
