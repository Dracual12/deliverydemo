from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from config import dp, bot, db
import handlers.stop_lists as sl
import handlers.auxiliary_functions as af
from handlers import send_table
import sys
import os

# Добавляем путь к корневой папке для импорта webapp_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



def boss_menu():
    menu = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text="⛔️СТОП-ЛИСТ", callback_data="boss_stop_list")
    btn2 = InlineKeyboardButton(text="📝ОФИЦИАНТЫ", callback_data="boss_waiters_stat")
    btn3 = InlineKeyboardButton(text="📶РЕКЛАМА", callback_data="boss_commercial")
    btn4 = InlineKeyboardButton(text="ТАБЛИЦА", callback_data="boss_table")
    
    # Добавляем кнопку Web App для админов
    
    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn3)
    menu.add(btn4)
    return menu


@dp.callback_query_handler(lambda call: call.data == "boss_commercial")
async def boss_commercial(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    text = ("<b>📶 РЕКЛАМА</b>\n\n"
            "Здесь будет статистика по рекламе и вовлеченности пользователей.\n\n"
            "Функции:\n"
            "• Статистика переходов\n"
            "• Конверсия пользователей\n"
            "• Аналитика по источникам трафика\n"
            "• Эффективность рекламных кампаний")
    
    keyboard = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_boss_menu")
    keyboard.add(back_btn)
    
    await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )


@dp.callback_query_handler(lambda call: call.data == "boss_waiters_stat")
async def boss_waiters_stat(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    
    # Получаем статистику официантов
    waiters = db.get_all_waiters()
    
    text = "<b>📝 СТАТИСТИКА ОФИЦИАНТОВ</b>\n\n"
    
    if waiters:
        for waiter in waiters:
            waiter_id = waiter[0]
            waiter_name = waiter[1] if len(waiter) > 1 else f"Официант {waiter_id}"
            earnings = db.get_current_earnings(waiter_id) or 0
            orders_count = len(eval(db.get_waiter_score(waiter_id))) if db.get_waiter_score(waiter_id) else 0
            
            text += f"<b>{waiter_name}</b>\n"
            text += f"• Заказов: {orders_count}\n"
            text += f"• Заработок: {earnings} руб.\n\n"
    else:
        text += "Официанты не найдены"
    
    keyboard = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_boss_menu")
    keyboard.add(back_btn)
    
    await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )


@dp.callback_query_handler(lambda call: call.data == "back_to_boss_menu")
async def back_to_boss_menu(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id

    await generate_boss_menu(call.from_user.id, None)


async def generate_boss_menu(boss_id, message_id=None):
    mes = db.get_users_temp_message_id(boss_id)
    text = ("<b>Привет!</b> 👋\n\n"
            f"*️⃣ Это панель управления <b>для менеджера</b> заведения <b>KoreanChick</b>\n\n"
            "<b><i>/СТОП-ЛИСТ</i></b> - добавление блюд в стоп-лист\n"
            "<b><i>/ОФИЦИАНТЫ</i></b> - статистика по работе официантов\n"
            "<b><i>/РЕКЛАМА</i></b> - статистика вовлеченности пользователей\n"
            "<b><i>/ТАБЛИЦА</i></b> - полный отчет о пользователях\n"
            "<b><i>/ВЕБ-ПРИЛОЖЕНИЕ</i></b> - открыть веб-интерфейс")
    if message_id:
        message_obj = await bot.edit_message_text(chat_id=boss_id,
                                                  message_id=mes[0],
                                                  text=text,
                                                  reply_markup=boss_menu())
    else:
        message_obj = await bot.send_message(
            chat_id=boss_id,
            text=text,
            reply_markup=boss_menu()
        )
    db.set_temp_users_message_id(boss_id, message_obj.message_id)


@dp.callback_query_handler(lambda call: call.data == "boss_table")
async def table(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    
    # Отправляем таблицу
    await send_table.send_table(call.message)


@dp.callback_query_handler(lambda call: call.data == "boss_stop_list")
async def boss_stop_list(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    
    # Переходим к управлению стоп-листом
    await sl.show_stop_list_menu(user, call.message.message_id)
