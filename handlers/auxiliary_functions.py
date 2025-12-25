import datetime
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from naim.main import db
from iiko_f.iiko import korean_chick_portion_price_range


def total_and_current_counter():
    stats = db.get_waiters_names_and_stats()
    last_check_time = db.get_last_check_time()
    if last_check_time == datetime.datetime.now().strftime("%Y-%m-%d"):
        current_click_count = db.get_current_click_count()
    else:
        current_click_count = 0
        db.set_current_click_count(current_click_count)

    db.set_last_check_time(datetime.datetime.now().strftime("%Y-%m-%d"))
    current_guests_count = db.get_current_guests_count()
    total_guests_count = 0
    total_click_count = db.get_total_click_count()
    for waiter in stats:
        if waiter[4]:
            total_guests_count += len(set(eval(waiter[4])))
    return total_click_count, current_click_count, total_guests_count, current_guests_count


def ind_to_number(ind):
    numbers = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    result = ""
    for char in str(ind):
        result += numbers[int(char)]
    return result


def update_total_and_current_counter():
    try:
        total_click_count = int(db.get_total_click_count())
        total_click_count += 1
        db.set_total_click_count(total_click_count)
        last_check_time = db.get_last_check_time(rest)
        if last_check_time == datetime.datetime.now().strftime("%Y-%m-%d"):
            current_click_count = int(db.get_current_click_count(rest))
            current_click_count += 1
        else:
            current_click_count = 1
        db.set_current_click_count(rest, current_click_count)
        db.set_last_check_time(rest, datetime.datetime.now().strftime("%Y-%m-%d"))
    except Exception as e:
        print(e)


def generate_dish_text(user, icons, dish, length, numb, dish_id):
    # Получаем рейтинг пользователя для этого блюда
    user_rating = None
    try:
        result = db.cursor.execute("SELECT users_dish_coefficients FROM correlation_coefficient WHERE user_id = ?", (user,)).fetchone()
        if result and result[0]:
            user_ratings = eval(result[0])
            if str(dish_id) in user_ratings:
                rating_data = user_ratings[str(dish_id)]
                if isinstance(rating_data, dict):
                    user_rating = rating_data['rating']
                else:
                    user_rating = float(rating_data)
    except Exception as e:
        print(f"Error getting user rating: {e}")

    # Формируем строку со звездочками
    stars = ""
    if user_rating is not None:
        stars = " " + "⭐" * round(user_rating)
    restaurant = "Korean Chick"
    # Проверяем, является ли блюдо порционным из Korean Chick
    # Проверяем, содержит ли строка "Korean Chick" (для учета возможного формата "Korean Chick: адрес")
    is_korean_chick = "Korean Chick" in restaurant
    price_text = ""
    weight_text = ""
    
    if is_korean_chick and dish['Название'] in korean_chick_portion_price_range:
        price_range = korean_chick_portion_price_range[dish['Название']]
        price_text = f"💰 <i>Цена: {price_range} руб.</i>"
        # Для порционных товаров не показываем вес
        weight_text = ""
    else:
        price_text = f"💰 <i>Цена: {int(dish['Цена'])} руб.</i>"
        weight_text = f"⚖️ <i>Вес: {str(dish['Грамм']).replace('.0', '')} г.</i>"

    text = (f"—— {icons[dish['Категория']]} <b>{dish['Категория']}</b> ——\n"
            f"\n"
            f"{icons[length - numb]} <i>{dish['Название']}</i>{stars}\n\n"
            f"{price_text}\n"
            f"{weight_text}"
            f"\n\n"
            f"<i>Узнай больше, нажав /команду:</i>"
            f"\n"
            f"\n"
            f"🔢/kbzhu - КБЖУ блюда"
            f"\n"
            f"🧾/sostav - состав блюда"
            f"\n"
            f"\n"
            f"<i>Листай блюда с помощью кнопок ⏪ и ⏩👇🏻</i>\n\n")
    if db.get_qr_scanned(user):
        text += "<b>Понравилось блюдо? Добавь его в корзину! 🛒</b>"
    return text
