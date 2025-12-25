import os
import asyncio
import time

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import dp, bot, db
from aiogram import types
import naim.normal as normal
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from naim.start_bot import buttons_start_02
from handlers import bosses
from menu import sort_the
import handlers.auxiliary_functions as af
from files.icons import icons
from waiters import waiter_start as w_start

# Кэш для списка файлов
_photo_files_cache = None
_photo_files_cache_time = 0
CACHE_TTL = 300  # 5 минут


def _get_photo_files_sync(photo_dir):
    """Синхронная функция для получения списка файлов"""
    return {os.path.splitext(file)[0]: os.path.join(photo_dir, file) 
            for file in os.listdir(photo_dir)}


async def get_photo_files(photo_dir):
    """Асинхронная функция для получения списка файлов с кэшированием"""
    global _photo_files_cache, _photo_files_cache_time
    
    current_time = time.time()
    # Обновляем кэш если он устарел или отсутствует
    if _photo_files_cache is None or (current_time - _photo_files_cache_time) > CACHE_TTL:
        _photo_files_cache = await asyncio.to_thread(_get_photo_files_sync, photo_dir)
        _photo_files_cache_time = current_time
    
    return _photo_files_cache









@dp.message_handler(commands=['kbzhu'])
async def kbzhu(message: types.Message):
    user = message.from_user.id
    message = message.message_id
    mes = db.get_users_temp_message_id(user)
    await bot.delete_message(chat_id=user, message_id=message)
    try:
        await bot.delete_message(chat_id=user, message_id=mes[0])
    except Exception as e:
        print(e)
    dish, length, numb = sort_the.get_dish(user)
    kb = dish['КБЖУ']

    try:
        message_obj = await bot.send_message(user,
                                                 f"📝КБЖУ блюда :\n <tg-spoiler><i>{kb}</i></tg-spoiler>\n",
                                                 reply_markup=return_after_dish_info())
    except:
        message_obj = await bot.send_message(user,
                                             f"📝Мы пока не обладаем информацией о КБЖУ данного блюда\n",
                                             reply_markup=return_after_dish_info())
    db.set_temp_users_message_id(user, message_obj.message_id)


@dp.message_handler(commands=['com'])
async def com(message: types.Message):
    user = message.from_user.id
    message = message.message_id
    mes = db.get_users_temp_message_id(user)
    await bot.delete_message(chat_id=user, message_id=message)
    await bot.delete_message(chat_id=user, message_id=mes[0])
    dish, length, numb = sort_the.get_dish(user)
    if dish['Описание']:
        message_obj = await bot.send_message(user,
                                             f"<blockquote><i>👨🏼‍⚕️: {dish['Описание'].split(';')[0]}</i></blockquote>\n\n",
                                             reply_markup=return_after_dish_info())
    else:
        message_obj = await bot.send_message(user,
                                             f"<blockquote><i>👨🏼‍⚕️: {dish['Описание']}</i></blockquote>\n\n",
                                             reply_markup=return_after_dish_info())
    db.set_temp_users_message_id(user, message_obj.message_id)



@dp.message_handler(commands=['sostav'])
async def com(message: types.Message):
    user = message.from_user.id
    message = message.message_id
    mes = db.get_users_temp_message_id(user)
    await bot.delete_message(chat_id=user, message_id=message)
    try:
        await bot.delete_message(chat_id=user, message_id=mes[0])
    except Exception as e:
        print(e)
    dish, length, numb = sort_the.get_dish(user)

    if dish['Ингредиенты'] is not None:
        message_obj = await bot.send_message(user,
                                             text=f"📝Состав блюда :\n <i>{', '.join(dish['Ингредиенты']).capitalize()}</i>\n",
                                             reply_markup=return_after_dish_info())
    else:
        message_obj = await bot.send_message(user,
                                             text=f"📝Состав блюда :\n <i>{str(db.get_dish_simple_sostav(dish['Ресторан'], dish['Название'])).capitalize()}</i>\n",
                                             reply_markup=return_after_dish_info())
    db.set_temp_users_message_id(user, message_obj.message_id)


def return_after_dish_info():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="return_to_dishes"))


@dp.callback_query_handler(text_contains=f"return_to_dishes")
async def return_to_dishes(call: types.CallbackQuery):
    # ВАЖНО: Отвечаем на callback query СРАЗУ, до любых долгих операций
    await call.answer()
    user = call.from_user.id
    dish, length, numb = sort_the.get_dish(user)
    dish_id = db.get_temp_users_dish_id(user)
    size_list = dish['Размер']
    photo_dir = '/srv/app/Food2Mood-demo/chick'

    # Используем асинхронную функцию для получения списка файлов
    all_files = await get_photo_files(photo_dir)
    
    shemodi_dish_photo = False
    photo_shemodi = ''
    for j in all_files:
        if j in dish['Название'] or dish['Название'] in j:
            shemodi_dish_photo = True
            photo_shemodi = j
    if size_list:
        size_list = eval(size_list)
    if db.check_basket_exists(user):
        basket = eval(db.get_basket(user))
        if dish['Название'] in basket:
            in_basket = True
            quantity = basket[dish['Название']][1]
        else:
            in_basket = False
            quantity = 0
    else:
        in_basket = False
        quantity = 0
    if shemodi_dish_photo or (dish['Название'] in all_files and dish['Ресторан'] == 'Молодёжь'):
        if shemodi_dish_photo:
            file_path = all_files[photo_shemodi]
        else:
            file_path = all_files[dish['Название']]
        
        # Проверяем существование файла асинхронно
        file_exists = await asyncio.to_thread(os.path.isfile, file_path)
        if file_exists:
            await bot.delete_message(chat_id=user, message_id=call.message.message_id)
            text = af.generate_dish_text(user, icons, dish, length, numb, dish_id)
            
            # Открываем файл асинхронно
            def open_file_sync(path):
                return open(path, 'rb')
            
            f = await asyncio.to_thread(open_file_sync, file_path)
            try:
                message_obj = await bot.send_photo(user, f,
                                                   caption=text,
                                                   reply_markup=buttons_food_05(dish_id,
                                                                              db.get_client_temp_dish(user),
                                                                                length, numb, in_basket,
                                                                                bool(db.get_qr_scanned(user)), quantity,
                                                                                size_list, user))
                db.set_temp_users_message_id(user, message_obj.message_id)
            finally:
                f.close()

# ======================================================================================================================
# ===== Создание клавиатур =================================================================================================
# ======================================================================================================================

def create_confirmation_buttons():
    menu = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text="Да, всё верно 👍🏻",
                                callback_data="blacklist_yes")

    btn2 = InlineKeyboardButton(text="Нет! Перепишу 👎🏻",
                                callback_data="blacklist_no")

    menu.row(btn1, btn2)

    return menu


def create_confirmation_buttons2():
    menu = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text="Да, всё верно 👍🏻",
                                callback_data="whitelist_yes")

    btn2 = InlineKeyboardButton(text="Нет! Перепишу 👎🏻",
                                callback_data="whitelist_no")

    menu.row(btn1, btn2)

    return menu


def create_web_app_button():
    webapp_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    webapp_keyboard.add(
        KeyboardButton(
            text="Открыть WebApp",
            url='http://t.me/koreanchickbot/F2M'
        )
    )
    return webapp_keyboard


async def choose_dish(dish_id, message: types.Message):
    user = message.from_user.id
    if db.get_users_ban(user):
        return None

    # Действие:
    dish = db.restaurants_get_by_id(dish_id)

    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=db.get_users_temp_message_id(user)[0],
        text=f"💫 Блюдо:\n"
             f"<i>«{dish[2]}»</i>\n"
             f"\n"
             f"Оцените блюдо по шкале от 1 до 5 👇🏻",
        reply_markup=buttons_04(dish_id)
    )


def buttons_04(dish_id):
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="1 ⭐",
                                callback_data=f"review_stat_1_{dish_id}")

    btn2 = InlineKeyboardButton(text="2 ⭐",
                                callback_data=f"review_stat_2_{dish_id}")

    btn3 = InlineKeyboardButton(text="3 ⭐",
                                callback_data=f"review_stat_3_{dish_id}")

    btn4 = InlineKeyboardButton(text="4 ⭐",
                                callback_data=f"review_stat_4_{dish_id}")

    btn5 = InlineKeyboardButton(text="5 ⭐",
                                callback_data=f"review_stat_5_{dish_id}")

    menu.row(btn1, btn2, btn3, btn4, btn5)

    return menu


@dp.callback_query_handler(text_contains="review_stat")
async def review_star(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    data = call.data.split('_')
    rating = data[-2]
    # await dp.storage.set_data(user=user, data={'rating': rating})

    if db.get_users_ban(user):
        return None

        # Действие:
    dish_id = int(data[-1])
    dish = db.restaurants_get_by_id(dish_id)
    db.restaurants_set_rating(dish_id, int(data[-2]))

    # Сохраняем оценку в таблицу correlation_coefficients
    db.save_dish_rating(user, dish_id, int(data[-2]))

    # Сбрасываем индекс текущего блюда, чтобы после оценки показ начинался с начала отсортированного списка
    try:
        db.set_client_temp_dish(user, 0)
    except Exception as e:
        print("reset numb error", e)

    await dp.storage.set_data(user=user, data={
        'rating': rating,
        'dish_name': dish[2],
    })

    # Удаление предыдущего сообщения
    await call.message.delete()

    message_obj = await bot.send_message(
        chat_id=user,
        text=f"💫 Блюдо:\n"
             f"<i>«{dish[2]}»</i>\n"
             f"\n"
             f"Если хотите оставить письменный отзыв, напиши его в ответ на это сообщение 🙏🏻\n"
             f"\n"
             f"Спасибо!",
        reply_markup=buttons_05()
    )
    db.set_temp_users_state(user, 'review_end')
    db.set_temp_users_message_id(user, message_obj.message_id)
    db.add_user_action(user, 'Пользователь оставил отзыв')


def buttons_05():
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="Пропустить ❌",
                                callback_data=f"review_end")

    menu.row(btn1)

    return menu


def buttons_food_05(dish_id: int, dish: int, length: int, last: int, in_basket: bool = None, qr_scanned: bool = None, quantity: int = 0, size_list: list = None, user: int = 0):
    menu = InlineKeyboardMarkup(row_width=3)
    qr_scanned = True
    if dish is not None:
        if length != 1:
            if dish > 0:
                btn1 = InlineKeyboardButton(text=f"⏪",
                                            callback_data="send_dish_back")

                if last == 0:
                    menu.row(btn1)
                else:
                    btn2 = InlineKeyboardButton(text=f"⏩",
                                                callback_data="send_dish_next")
                    menu.row(btn1, btn2)
            else:
                btn2 = InlineKeyboardButton(text=f"⏩",
                                            callback_data="send_dish_next")
                menu.add(btn2)
        if qr_scanned:
            if in_basket:
                if quantity > 1:
                    btn0 = InlineKeyboardButton(text=f"Убрать из 🛒 ({quantity})",
                                                callback_data=f"basket_remove")
                else:
                    btn0 = InlineKeyboardButton(text="Убрать из 🛒",
                                                callback_data=f"basket_remove")
                if size_list:
                    btn_extra = InlineKeyboardButton(text="+ 1",
                                                     callback_data=f"choice_size_{dish_id}")
                else:
                    btn_extra = InlineKeyboardButton(text="+ 1",
                                                callback_data=f"basket_add")
                menu.add(btn0)
                menu.add(btn_extra)
            else:
                if size_list:
                    btn0 = InlineKeyboardButton(text="Добавить в 🛒",
                                                callback_data=f"choice_size_{dish_id}")
                else:
                    btn0 = InlineKeyboardButton(text="Добавить в 🛒",
                                                callback_data=f"basket_add")
                menu.add(btn0)
            btn3 = InlineKeyboardButton(text="Перейти к ➡️ 🛒", callback_data="check_order")
            menu.add(btn3)
    # menu_start
    btn1 = InlineKeyboardButton(text="⬅️ Вернуться к категориям",
                                callback_data="watch_menu_again")

    menu.add(btn1)
    return menu


@dp.message_handler(commands=['boss'])
async def boss_shemodi(message: types.Message):
    user = message.from_user.id
    await bot.delete_message(user, message.message_id)
    message_obj = await bot.send_message(
        chat_id=user,
        text="Введите пароль: ",
    )
    db.set_temp_users_state(user, 'boss')
    db.set_temp_users_message_id(user, message_obj.message_id)


@dp.callback_query_handler(text_contains="review_end")
async def review_end(call: types.CallbackQuery):
    await call.answer()
    user_first_name = db.get_users_user_first_name(call.from_user.id)
    await bot.edit_message_text(chat_id=call.from_user.id,
                                message_id=call.message.message_id,
                                text=f"<b>{user_first_name}</b>, оставь отзыв о выбранных блюдах в ресторане <b>Korean Chick</b> \n\n"
                                     f"Нейросеть food2mood учтёт твои комментарии при формировании персональных рекомендаций в будущем 😏🔜",
                                reply_markup=buttons_02()
    )


def buttons_02():
    menu = InlineKeyboardMarkup(row_width=2)

    btn1 = InlineKeyboardButton(text="⏮️ Вернуться на главную",
                                callback_data="menu_start")

    btn2 = InlineKeyboardButton(text="Оставить ещё один отзыв 🆕", callback_data="leave_a_review")

    btn3 = InlineKeyboardButton(text="Мои f2m коины 🪙", callback_data="food_to_mood_coin_status")

    menu.add(btn1)
    menu.add(btn2)

    return menu


@dp.callback_query_handler(text_contains='menu_start')
async def return_to_start(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    text = (f"<b>Привет, дорогой друг!\n"
            "Как ты хочешь сделать заказ? </b>☺️🙏")
    await call.message.delete()
    message_obj = await bot.send_message(
        chat_id=user,
        text=text,
        parse_mode='HTML',
        reply_markup=buttons_start_02()
    )