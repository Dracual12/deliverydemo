import ast
import os
import time
import asyncio

from config import db, dp, bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

from iiko_f.iiko import korean_chick_portion_price
from menu import sort_the
import handlers.auxiliary_functions as af
from files.icons import icons

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

# ======================================================================================================================
# ===== Обработка callbacks =================================================================================================
# ======================================================================================================================


@dp.callback_query_handler(text_contains='watch_menu')
async def watch_menu(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    text = 'Выбери категорию меню 🔍'
    if 'again' in call.data:
        await bot.delete_message(chat_id=user, message_id=call.message.message_id)
        await bot.send_message(chat_id=user, text=text, reply_markup=create_menu_buttons())
    else:

        await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text=text,
                                reply_markup=create_menu_buttons())


@dp.callback_query_handler(text_contains='category_menu')
async def category_menu(call: types.CallbackQuery):
    # ВАЖНО: Отвечаем на callback query СРАЗУ, до любых долгих операций
    await call.answer()
    category = call.data.split('_')[-1]
    user = call.from_user.id
    await bot.delete_message(chat_id=user, message_id=call.message.message_id)
    # Если предполагается, что название категории может содержать подчеркивания
    if category:  # Проверка на наличие категории
        db.set_temp_users_category(user, category)
    db.set_client_temp_dish(user, 0)
    dish, length, numb = sort_the.get_dish(user)
    try:
        dish_id = db.restaurants_get_dish(dish['Название'])[0]
    except Exception as e:
        dish_id = None

    if dish is not None:
        text = af.generate_dish_text(user, icons, dish, length, numb, dish_id)
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
        size_list = dish['Размер']
        if size_list:
            size_list = eval(size_list)
        photo_dir = '/srv/app/Food2Mood-demo/chick'

        # Используем асинхронную функцию для получения списка файлов
        all_files = await get_photo_files(photo_dir)
        
        shemodi_dish_photo = False
        photo_shemodi = ''
        for j in all_files:
            if j in dish['Название'] or dish['Название'] in j:
                shemodi_dish_photo = True
                photo_shemodi = j
        if shemodi_dish_photo or (dish['Название'] in all_files and dish['Ресторан'] == 'Молодёжь'):
            if shemodi_dish_photo:
                file_path = all_files[photo_shemodi]
            else:
                file_path = all_files[dish['Название']]
            
            # Проверяем существование файла асинхронно
            file_exists = await asyncio.to_thread(os.path.isfile, file_path)
            if file_exists:
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
                finally:
                    f.close()
            else:
                message_obj = await bot.send_message(
                    chat_id=user,
                    text=text,
                    reply_markup=buttons_food_05(dish_id, db.get_client_temp_dish(user), length, numb, in_basket,
                                                 bool(db.get_qr_scanned(user)), quantity, size_list, user)
                )
        else:
            message_obj = await bot.send_message(
                chat_id=user,
                text=text,
                reply_markup=buttons_food_05(dish_id, db.get_client_temp_dish(user), length, numb, in_basket,
                                             bool(db.get_qr_scanned(user)), quantity, size_list, user)
            )
        db.set_temp_users_dish_id(user, db.restaurants_get_dish(dish['Название'])[0])

    else:
        message_obj = await bot.send_message(
            chat_id=user,
            text=f"🍤"
                 f"<b>Кажется, в этом заведении нет блюд, подходящих под ваши критерии</b> 🤔\n"
                 f"\n"
                 f"Попробуй поменять категорию блюд, настроение или список продуктов, которые ты не употребляешь в пищу 😉\n",
            reply_markup=create_back_to_cat_buttons()
        )
    db.set_temp_users_message_id(user, message_obj.message_id)


# ======================================================================================================================
# ===== Создание клавиатур =================================================================================================
# ======================================================================================================================

def create_back_to_cat_buttons():
    menu = InlineKeyboardMarkup()
    back_btn = InlineKeyboardButton(text="⬅️ Назад", callback_data='watch_menu')
    menu.add(back_btn)
    return menu


def create_menu_buttons():
    menu = InlineKeyboardMarkup()
    for e in db.get_all_categories():
        menu.add(InlineKeyboardButton(text=f"{e} {icons[e]}",
                                      callback_data=f"category_menu_{e}"))
    back_btn = InlineKeyboardButton(text="⬅️ Назад",
                                    callback_data="back_to_start")
    menu.add(back_btn)
    return menu


def create_buttons_to_menu(user):
    menu = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text=f"Ознакомиться с меню 🧾",
                                callback_data=f"watch_menu")
    btn2 = InlineKeyboardButton(text="⬅️ Назад",
                                callback_data="back_to_start")
    menu.add(btn1)
    menu.add(btn2)
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


@dp.callback_query_handler(text_contains=f"choice_size")
async def choice_size(call: types.CallbackQuery):
    await call.answer()
    try:
        user = call.from_user.id
        text = "<b>Выбери размер порции:</b>"
        dish_id = int(call.data.split("_")[-1])


        # Получаем информацию о блюде
        dish_data = db.restaurants_get_by_id(dish_id)
        if not dish_data or len(dish_data) < 5:
            await bot.answer_callback_query(call.id, "Ошибка: информация о блюде не найдена", show_alert=True)
            return

        dish_name = dish_data[2]

        # Получаем список доступных размеров
        size_list = db.get_dish_size(dish_id)
        if not size_list:
            await bot.answer_callback_query(call.id, "Ошибка: размеры порций не найдены", show_alert=True)
            return

        # Создаем клавиатуру с размерами
        keyboard = size_keyboard(size_list, dish_name)
        # Отправляем сообщение с выбором размера
        await bot.delete_message(
            chat_id=user,
            message_id=call.message.message_id)
        await bot.send_message(chat_id=user,
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    except Exception as e:
        # logger.error(f"Error in choice_size: {str(e)}")
        print(e)
        await bot.answer_callback_query(call.id, "Произошла ошибка при выборе размера", show_alert=True)


def size_keyboard(size_list, dish_name=None):
    keyboard = InlineKeyboardMarkup(row_width=1)
    size_list = ast.literal_eval(size_list)
    for size in size_list:
        if dish_name and size.startswith(dish_name):
            # Для Korean Chick показываем только размер и цену
            display_text = size.replace(dish_name, '').strip() + f" ({korean_chick_portion_price[size]} руб.)"
            btn = InlineKeyboardButton(text=display_text,
                                       callback_data=f"basket_add_{size}")
        else:
            btn = InlineKeyboardButton(text=f"{size}",
                                       callback_data=f"basket_add_{size}")
        keyboard.row(btn)
    return keyboard



