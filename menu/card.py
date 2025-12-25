import asyncio
import tempfile
import time

import qrcode

from iiko_f.iiko import korean_chick_portion_price
from aiogram.types import InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from config import dp, db, bot
from aiogram import types
from files.icons import icons
import os
from handlers import auxiliary_functions as af
import menu.sort_the as sort_the
from aiogram.utils.deep_linking import get_start_link
from menu.categories import buttons_food_05, create_menu_buttons, create_buttons_to_menu

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


@dp.callback_query_handler(text_contains=f"send_dish")
async def send_dish(call: types.CallbackQuery):
    # ВАЖНО: Отвечаем на callback query СРАЗУ, до любых долгих операций
    await call.answer()
    try:
        user = call.from_user.id
        data = call.data.split('_')
        if db.get_users_ban(user):
            return None
        foods_photo_for_category_message_id = db.get_users_temp_message_id(user)
        if "del" in data[-1]:
            try:
                message_id = call.data.split("send_dish_del")[-1]
                await bot.delete_message(user, int(message_id))
            except TypeError:
                pass
            except Exception as e:
                print(e)

        # Действие:

        if data[-1] == 'next':
            db.set_client_temp_dish(user, db.get_client_temp_dish(user) + 1)
        elif data[-1] == 'back':
            db.set_client_temp_dish(user, db.get_client_temp_dish(user) - 1)

        dish, length, numb = sort_the.get_dish(user)

        dish_id = db.restaurants_get_dish(dish['Название'])[0]
        size_list = dish['Размер']
        if size_list:
            size_list = eval(size_list)
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
        
        # Используем асинхронную функцию для получения списка файлов
        photo_dir = '/srv/app/Food2Mood-demo/chick'
        all_files = await get_photo_files(photo_dir)
        
        message_obj = None
        last_message = foods_photo_for_category_message_id
        if 'photo' in last_message:
            flag = False
            for j in all_files:
                if j in dish['Название']:
                    flag = True
                    file_path = all_files[j]
                    # Открываем файл асинхронно
                    def open_file_sync(path):
                        return open(path, 'rb')
                    
                    f = await asyncio.to_thread(open_file_sync, file_path)
                    try:
                        photo = InputMediaPhoto(media=f, caption=text)
                        # Проверяем существование файла асинхронно
                        file_exists = await asyncio.to_thread(os.path.isfile, file_path)
                        if file_exists:
                            message_obj = await bot.edit_message_media(chat_id=user,
                                                                       message_id=call.message.message_id,
                                                                       media=photo,
                                                                       reply_markup=buttons_food_05(dish_id,
                                                                                                    db.get_client_temp_dish(
                                                                                                        user),
                                                                                                    length, numb,
                                                                                                    in_basket, bool(
                                                                               db.get_qr_scanned(user)), quantity,
                                                                                                    size_list, user))

                            foods_photo_for_category_message_id = message_obj
                    finally:
                        f.close()
            if not flag:
                await bot.delete_message(chat_id=user, message_id=call.message.message_id)
                message_obj = await bot.send_message(
                    chat_id=user,
                    text=text,
                    reply_markup=buttons_food_05(dish_id, db.get_client_temp_dish(user), length, numb, in_basket,
                                                 bool(db.get_qr_scanned(user)), quantity, size_list, user)
                )
                foods_photo_for_category_message_id = message_obj
        else:
            flag = False
            for j in all_files:
                if j in dish['Название']:
                    flag = True
                    file_path = all_files[j]

                    # Открываем файл асинхронно
                    def open_file_sync(path):
                        return open(path, 'rb')
                    
                    f = await asyncio.to_thread(open_file_sync, file_path)
                    try:
                        file_exists = await asyncio.to_thread(os.path.isfile, file_path)
                        if file_exists:
                            await bot.delete_message(chat_id=user, message_id=call.message.message_id)
                            message_obj = await bot.send_photo(user, f, caption=text,
                                                               reply_markup=buttons_food_05(dish_id,
                                                                                            db.get_client_temp_dish(
                                                                                                user),
                                                                                            length, numb,
                                                                                            in_basket, bool(
                                                                       db.get_qr_scanned(user)), quantity, size_list,
                                                                                            user))
                            foods_photo_for_category_message_id = message_obj
                    finally:
                        f.close()
            if not flag:
                message_obj = await bot.edit_message_text(
                    chat_id=user,
                    message_id=call.message.message_id,
                    text=text,
                    reply_markup=buttons_food_05(dish_id, db.get_client_temp_dish(user), length, numb, in_basket,
                                                 bool(db.get_qr_scanned(user)), quantity, size_list, user)
                )
                foods_photo_for_category_message_id = message_obj
        db.set_temp_users_message_id(user, foods_photo_for_category_message_id.message_id)
        db.set_temp_users_dish_id(user, db.restaurants_get_dish(dish['Название'])[0])
    except Exception as e:
        print(f"Error in send_dish: {e}")
        import traceback
        traceback.print_exc()


@dp.callback_query_handler(text_contains=f"basket")
async def change_basket(call: types.CallbackQuery):
    await call.answer()
    try:
        user = call.from_user.id
        if not db.check_basket_exists(user):
            db.create_basket(user)
        basket_mode = call.data.split("basket_")[-1]

        # Получаем информацию о блюде
        dish_info = sort_the.get_dish(user)
        if dish_info is None:
            await bot.answer_callback_query(call.id, "Ошибка: информация о блюде не найдена", show_alert=True)
            return

        dish, length, numb = dish_info
        if dish is None or not isinstance(dish, dict):
            await bot.answer_callback_query(call.id, "Ошибка: неверный формат данных блюда", show_alert=True)
            return

        # Получаем ID блюда
        dish_id_data = db.restaurants_get_dish(dish['Название'])
        if not dish_id_data:
            await bot.answer_callback_query(call.id, "Ошибка: ID блюда не найден", show_alert=True)
            return

        dish_id = dish_id_data[0]
        if not dish_id:
            await bot.answer_callback_query(call.id, "Ошибка: ID блюда не найден", show_alert=True)
            return

        size_check = basket_mode.split("_")
        if len(size_check) > 1:
            size = size_check[-1]
            text = af.generate_dish_text(user, icons, dish, length, numb, dish_id)
        else:
            size = None
            text = ""

        # Получаем информацию о блюде из базы данных
        dish_data = db.restaurants_get_by_id(dish_id)
        if not dish_data or len(dish_data) < 5:
            await bot.answer_callback_query(call.id, "Ошибка: информация о блюде не найдена", show_alert=True)
            return
        dish_name = dish_data[2]
        size_list = dish_data[21] if len(dish_data) > 21 else None

        if size_list:
            try:
                size_list = eval(size_list)
            except:
                size_list = None

        basket = eval(db.get_basket(user))
        restaurant_name = "Korean Chick"
        # Формируем полное название для Korean Chick
        if "Korean Chick" in restaurant_name and size:
            full_dish_name = f"{dish_name} {size}"
        else:
            full_dish_name = dish_name

        if "add" in basket_mode:
            if full_dish_name not in basket:
                basket[full_dish_name] = [dish_id, 1, [size]]
            else:
                basket[full_dish_name][1] += 1
                basket[full_dish_name][2].append(size)
            in_basket = True
            quantity = basket[full_dish_name][1]
        else:
            if full_dish_name in basket and basket[full_dish_name][1] > 1:
                basket[full_dish_name][1] -= 1
                in_basket = True
                quantity = basket[full_dish_name][1]
                basket[full_dish_name][2].pop()
            else:
                basket.pop(full_dish_name, None)
                in_basket = False
                quantity = 0

        db.set_basket(user, str(basket))

        if text:
            # Проверяем, есть ли фото в сообщении
            if call.message.photo:
                # Если есть фото, редактируем caption
                await bot.edit_message_caption(
                    chat_id=user,
                    message_id=call.message.message_id,
                    caption=text,
                    reply_markup=buttons_food_05(dish_id, db.get_client_temp_dish(user), length, numb, in_basket,
                                                 bool(db.get_qr_scanned(user)), quantity, size_list, user))
            else:
                # Если фото нет, удаляем сообщение и отправляем новое
                await bot.delete_message(chat_id=user, message_id=call.message.message_id)
                message_obj = await bot.send_message(
                    chat_id=user,
                    text=text,
                    reply_markup=buttons_food_05(dish_id, db.get_client_temp_dish(user), length, numb, in_basket,
                                                 bool(db.get_qr_scanned(user)), quantity, size_list, user)
                )
                db.set_users_mode(user, message_obj.message_id, 'choose_dish_size')
        else:
            await bot.edit_message_reply_markup(
                chat_id=user,
                message_id=call.message.message_id,
                reply_markup=buttons_food_05(dish_id, db.get_client_temp_dish(user), length, numb, in_basket,
                                             bool(db.get_qr_scanned(user)), quantity, size_list, user))
    except Exception as e:
        print(f"Error in change_basket: {e}")
        await bot.answer_callback_query(call.id, "Произошла ошибка при изменении корзины", show_alert=True)


@dp.callback_query_handler(text_contains=f"check_order")
async def check_order(call: types.CallbackQuery):
    await call.answer()
    state = False
    try:
        if '2' in call.data:
            state = True
        user = call.from_user.id
        basket_cost = calc_basket_cost(user)
        # Логируем сумму заказа в сессии
        db.update_logging_session_sum(str(user), basket_cost)
        text = "❗️<b>Проверь корзину, перед тем как сделать заказ</b> ❗️\n\n" \
               f"<i><b>Нажми на позицию</b>, чтобы убрать ее из корзины {icons['Крест']}\n" \
               "<b>Вернись к категориям</b>, чтобы добавить еще блюда </i>\n\n" \
               f"<i><b>🛒ИТОГО</b>: {basket_cost} руб.</i>"
        await bot.delete_message(chat_id=user, message_id=call.message.message_id)
        message_obj = await bot.send_message(chat_id=user, text=text, reply_markup=generate_basket(user, state))
    except Exception as e:
        print("order error", e)


def get_basket_items(user):
    """Получить список блюд в корзине"""
    items = []
    if db.check_basket_exists(user):
        basket = eval(db.get_basket(user))
        for dish_name in basket:
            quantity = basket[dish_name][1]
            if quantity > 1:
                items.append(f"{dish_name} x{quantity}")
            else:
                items.append(dish_name)
    return items

def calc_basket_cost(user):
    summary = 0
    if db.check_basket_exists(user):
        basket = eval(db.get_basket(user))
        restaurant = "Korean Chick"

        for dish_name in basket:
            # Проверяем, является ли ресторан Korean Chick
            if "Korean Chick" in restaurant:
                # Для Korean Chick проверяем полное название блюда (с размером)
                if len(basket[dish_name]) > 2 and basket[dish_name][2]:  # Проверяем, что есть размеры
                    # Считаем сумму для каждой порции
                    for size in basket[dish_name][2]:
                        full_dish_name = f"{dish_name} {size}"
                        if full_dish_name in korean_chick_portion_price:
                            # Берем цену из словаря порционных цен
                            price = int(korean_chick_portion_price[full_dish_name])
                            summary += price
                        else:
                            # Если блюдо не в словаре порционных цен, берем цену из базы
                            price = int(db.get_dish_price(basket[dish_name][0])[0][0])
                            summary += price
                else:
                    # Если нет размеров, берем цену из базы
                    price = int(db.get_dish_price(basket[dish_name][0])[0][0])
                    summary += price * basket[dish_name][1]
            else:
                # Для остальных ресторанов берем цену из базы
                price = int(db.get_dish_price(basket[dish_name][0])[0][0])
                summary += price * basket[dish_name][1]
    return summary


def generate_basket(user, state):
    try:
        if db.check_basket_exists(user):
            basket = eval(db.get_basket(user))
        else:
            basket = {}
        keyboard = InlineKeyboardMarkup(row_width=1)
        if len(basket) > 0:
            for dish in basket:
                if basket[dish][1] > 1:
                    btn = InlineKeyboardButton(text=f"{icons['Крест']} {dish} ({basket[dish][1]})",
                                               callback_data=f"delete_{basket[dish][0]}")
                else:
                    btn = InlineKeyboardButton(text=f"{icons['Крест']} {dish}",
                                               callback_data=f"delete_{basket[dish][0]}")
                keyboard.row(btn)
            if not state:
                btn2 = InlineKeyboardButton(text="⬅️ Вернуться к категориям", callback_data="watch_menu_again")
            else:
                btn2 = InlineKeyboardButton(text="⬅️ Вернуться к категориям", callback_data="watch_menu_again")
            btn1 = InlineKeyboardButton(text="ОФОРМИТЬ ЗАКАЗ ✅",
                                        callback_data='create_qr')
            keyboard.row(btn1)
            keyboard.row(btn2)
        else:
            btn0 = InlineKeyboardButton(text="⬅️ Ваша корзина пуста", callback_data="watch_menu_again")
            keyboard.row(btn0)
        return keyboard
    except Exception as e:
        print("generate error", e)



@dp.callback_query_handler(text_contains=f"delete")
async def change_basket(call: types.CallbackQuery):
    await call.answer()
    try:
        user = call.from_user.id
        dish_id = call.data.split("delete_")[-1]
        dish = db.restaurants_get_by_id(dish_id)[2]
        basket = eval(db.get_basket(user))
        if basket[dish][1] > 1:
            basket[dish][1] -= 1
        else:
            try:
                basket.pop(dish, None)
            except ValueError:
                pass
        db.set_basket(user, str(basket))
        basket_cost = calc_basket_cost(user)
        text = "❗️<b>Проверь корзину, перед тем как сделать заказ</b> ❗️\n\n" \
               "<i><b>Нажми на позицию</b>, чтобы убрать ее из корзины 🚫\n" \
               "<b>Вернись к категориям</b>, чтобы добавить еще блюда ➕</i>\n\n" \
               f"<i><b>🛒ИТОГО</b>: {basket_cost} руб.</i>"
        await bot.edit_message_text(
            chat_id=user,
            message_id=call.message.message_id,
            text=text,
            reply_markup=generate_basket(user, False))
    except Exception as e:
        print("basket error", e)




@dp.callback_query_handler(text_contains=f"create_qr")
async def create_qr(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    if db.get_users_ban(user):
        return None
    url = await get_start_link(f"or{user}", encode=True)
    try:
        # Получаем корзину пользователя
        basket = db.get_basket(user)
        if not basket or basket == "{}":
            await bot.answer_callback_query(call.id, "Ваша корзина пуста!", show_alert=True)
            return
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img.save(tmp_file.name)

            try:
                # Отправляем QR-код
                with open(tmp_file.name, 'rb') as photo:
                    await bot.delete_message(chat_id=user, message_id=call.message.message_id)
                    await bot.send_photo(
                        chat_id=user,
                        photo=photo,
                        caption="Покажите QR-код официанту/кассиру для оплаты заказа",
                        reply_markup=create_qr_keyboard(call.message.message_id)
                    )
                    # Логируем состав заказа в сессию
                    basket_items = get_basket_items(user)
                    order_composition = ", ".join(basket_items) if basket_items else "Корзина пуста"
                    db.update_logging_session_order(str(user), order_composition)
            except:
                pass
    except Exception as e:
        print(f"Error in create_qr: {e}")



def create_qr_keyboard(message_id):
    keyboard = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="Готово ✅",
                                callback_data=f"bon_appetite{message_id}")

    btn2 = InlineKeyboardButton(text="⬅️ Вернуться к категориям",
                                callback_data=f"watch_menu_again")

    keyboard.row(btn1)
    keyboard.row(btn2)
    return keyboard


@dp.callback_query_handler(text_contains='bon_appetite')
async def bon_appetite(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    mesage_id = call.message.message_id
    await bot.delete_message(chat_id=user, message_id=mesage_id)
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="1 ⭐",
                                callback_data=f"comment_review_star_1")

    btn2 = InlineKeyboardButton(text="2 ⭐",
                                callback_data=f"comment_review_star_2")

    btn3 = InlineKeyboardButton(text="3 ⭐",
                                callback_data=f"comment_review_star_3")

    btn4 = InlineKeyboardButton(text="4 ⭐",
                                callback_data=f"comment_review_star_4")

    btn5 = InlineKeyboardButton(text="5 ⭐",
                                callback_data=f"comment_review_star_5")

    menu.row(btn1, btn2, btn3, btn4, btn5)

    message_obj = await bot.send_message(
        chat_id=user,
        text=f"<b>Спасибо, что воспользовался сервисом <a href='https://t.me/food_2_mood'>food2mood</a>!❤️</b>\n\n"
             "Как вам наша рекомендации?",
        reply_markup=menu
    )




def bon_app_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="Оставить отзыв 📝",
                                callback_data=f"leave_a_review")

    btn2 = InlineKeyboardButton(text="⬅️ Вернуться к категориям",
                                callback_data=f"watch_menu_again")

    keyboard.row(btn1)
    keyboard.row(btn2)
    return keyboard


@dp.callback_query_handler(text_contains="leave_a_review")
async def leave_a_review_global(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id

    # Удаление предыдущего сообщения
    await call.message.delete()

    # Отправка нового сообщения с клавиатурой
    message = await bot.send_message(
        chat_id=user,
        text="Найдите блюдо в поиске 🔎",
        reply_markup=search_dish_keyboard()
    )

    db.set_temp_users_state(user, 'review')
    db.set_temp_users_message_id(user, message.message_id)


def search_dish_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)

    search_activate_button = InlineKeyboardButton(text="Поиск блюд 🔍", switch_inline_query_current_chat='')
    keyboard.add(search_activate_button)

    return keyboard


@dp.callback_query_handler(text_contains="comment_review_star")
async def like_reason(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    keyboard = InlineKeyboardMarkup(row_width=1)
    star = call.data[-1]
    btn1 = InlineKeyboardButton(text="Угадали с блюдом 🍛",
                                callback_data=f"comment2_right_dish" + star)

    btn2 = InlineKeyboardButton(text="Удобно пользоваться 👩🏻‍💻",
                                callback_data=f"comment2_comfort" + star)

    btn3 = InlineKeyboardButton(text="Большой выбор заведений 🏘",
                                callback_data=f"comment2_many_restaurants" + star)

    btn4 = InlineKeyboardButton(text="Большой выбор блюд 🍲",
                                callback_data=f"comment2_many_dishes" + star)

    btn5 = InlineKeyboardButton(text="Улучшили настроение 😄",
                                callback_data=f"comment2_mood_better" )
    btn6 = InlineKeyboardButton(text='Другое ⚠️',
                                callback_data='comment2_other_reason' + star)

    keyboard.add(btn1, btn2, btn3, btn4, btn5, btn6)
    message_obj = await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text= "Что именно понравилось?",
        reply_markup=keyboard
    )



@dp.callback_query_handler(text_contains="comment2")
async def reaction_on_comm(call: types.CallbackQuery):
    await call.answer()
    star = call.data[-1]
    if 'other' in call.data:
        await bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text='Пожалуйста, расскажите нам, что именно вам понравилось'
        )
    else:
        if 'better' in call.data:
            db.add_reason(call.from_user.id, 'Улучшили настроение', star)
        if 'dishes' in call.data:
            db.add_reason(call.from_user.id, 'Большой выбор блюд', star)
        if 'restauranta' in call.data:
            db.add_reason(call.from_user.id, 'Большой выбор заведений', star)
        if 'comfort' in call.data:
            db.add_reason(call.from_user.id, 'Удобно пользоваться', star)
        if 'right' in call.data:
            db.add_reason(call.from_user.id, 'Угадали с блюдом', star)

        message_obj = await bot.edit_message_text(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            text=f"<b>Спасибо! Вы добавили еще больше вкуса в наш сервис! 🍽️💡</b> \n ",
            reply_markup=bon_app_keyboard()
        )
        await asyncio.sleep(1)  # Подождать час
        try:
            await bot.delete_message(chat_id=call.from_user.id, message_id=message_obj.message_id)
        except:
            pass
        await send_reminder_message(call.from_user.id)  # Отправить напоминалку



async def send_reminder_message(user_id):
    user_first_name = db.get_users_user_first_name(user_id)
    keyboard = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text="Оставить отзыв", callback_data="leave_a_review")
    btn2 = InlineKeyboardButton(text="Не интересно", callback_data="menu_start")
    keyboard.add(btn1, btn2)

    await bot.send_message(
        chat_id=user_id,
        text=f"<b>{user_first_name}</b>, оставь отзыв о выбранных блюдах в ресторане <b>Korean Chick</b> \n\n"
             f"Нейросеть food2mood учтёт твои комментарии при формировании персональных рекомендаций в будущем 😏🔜",
        reply_markup=keyboard
    )


@dp.callback_query_handler(text_contains='return_to_recommendation')
async def return_to_recommendation(call: types.CallbackQuery):
    """Перенаправление на категории меню вместо рекомендаций"""
    await call.answer()
    user = call.from_user.id
    text = 'Выбери категорию меню 🔍'
    await bot.edit_message_text(
        chat_id=user,
        message_id=call.message.message_id,
        text=text,
        reply_markup=create_menu_buttons()
    )


