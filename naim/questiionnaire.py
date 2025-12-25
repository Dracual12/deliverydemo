from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from config import dp, bot, db
from files.icons import icons
from menu.categories import create_buttons_to_menu
from menu.sort_the import generate_recommendation
# ======================================================================================================================
# ===== Получение текста анкет =================================================================================================
# ======================================================================================================================


def make_the_first_q(user):
    ank = db.get_users_first_q(user)
    text = '<b>Как ты сейчас себя чувствуешь? </b>🙂🙌\n\n'
    text += '<b>——— Настроение ———</b>\n\n'
    text += f'{ank[1]} {icons[ank[1]]}\n\n'
    text += f'<b>——— Голоден на  ———</b>\n\n'
    text += f'\t{ank[2]}\n\n'
    text += '<b>——— Хочется что-то нового?  ———</b>\n\n'
    text += f'\t{ank[3]} {icons[ank[3]]}'
    return text


def buttons_for_the_first_q():
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="Всё так ✅",
                                callback_data="confirmation_of_the_first_q")

    btn2 = InlineKeyboardButton(text="Изменить анкету 📝",
                                callback_data="change_the_first_q")
    menu.add(btn1)
    menu.add(btn2)

    return menu


def make_the_second_q(user):
    ank = db.get_users_second_q(user)
    age2 = ank[2]
    age = ''
    if age2 == "До 18":
        age = "До 18 👶"
    elif age2 == "18-25":
        age = "18-25 🧑"
    elif age2 == "26-35":
        age = "26-35 👨‍🦱"
    elif age2 == "36-45":
        age = "36-45 🧔‍️"
    elif age2 == 'пусто':
        age = 'пусто'
    text = '<b>Анкета твоих вкусовых предпочтений</b> 📃\n\n'
    text += '<b>——— Пол ———</b>\n'
    text += f'{ank[1]} {icons[ank[1]]}️\n\n'
    text += '<b>——— Возраст ———</b>\n'
    text += f'{age}\n\n'
    text += '<b>——— Стиль питания ———</b>\n'
    text += f'{ank[3]} {icons[ank[3]]}\n\n'
    if ank[4] == 'пусто' or ank[4] is None:
        text += '<b>——— НЕ ЕШЬ 💔 ———</b>\n'
        text += f'{ank[5]}\n\n'
        text += '<b>——— ЛЮБИШЬ ❤️ ———</b>\n'
        text += f'{ank[6]}\n\n'
        text += '<blockquote>Кстати, food2mood <b>учитывает твой опыт</b> и может изменять профиль на основе отзывов. ' \
                '<b>Оставляй отзывы</b> на блюда после приема пищи для более четких рекомендаций в будущем 😉🙏</blockquote>'
    else:
        text += '<b>——— Ккал на блюдо ———</b>\n'
        text += f'{ank[4]}\n\n'
        text += '<b>——— НЕ ЕШЬ 💔 ———</b>\n'
        text += f'{ank[5]}\n\n'
        text += '<b>——— ЛЮБИШЬ ❤️ ———</b>\n'
        text += f'{ank[6]}\n\n'
        text += '<blockquote>Кстати, food2mood <b>учитывает твой опыт</b> и может изменять профиль на основе отзывов. ' \
                '<b>Оставляй отзывы</b> на блюда после приема пищи для более четких рекомендаций в будущем 😉🙏</blockquote>'

    return text


def buttons_for_the_second_q():
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="Всё так ✅",
                                callback_data="confirmation_of_the_second_q")

    btn2 = InlineKeyboardButton(text="Изменить анкету 📝",
                                callback_data="change_the_second_q")
    btn3 = InlineKeyboardButton(text="⬅️ Назад",
                                callback_data="order_at_rest_return")
    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn3)
    return menu


# ======================================================================================================================
# ===== Обработка callbacks =================================================================================================
# ======================================================================================================================


@dp.callback_query_handler(text_contains='confirmation_of_the')
async def confirmation_of_the_first_q(call: types.CallbackQuery):
    await call.answer()
    if 'first' in call.data:
        # Логируем все данные первой анкеты в сессию
        user_id = str(call.from_user.id)
        first_q_data = db.get_users_first_q(call.from_user.id)
        if first_q_data:
            db.update_logging_session_mood(user_id, first_q_data[1])  # настроение (индекс 1)
            db.update_logging_session_hungry(user_id, first_q_data[2])  # голод (индекс 2)
            db.update_logging_session_style(user_id, first_q_data[3])  # стиль (prefers, индекс 3)
        
        message_with_q = await bot.edit_message_text(chat_id=call.from_user.id,
                                                     message_id=call.message.message_id,
                                                     text=make_the_second_q(call.from_user.id),
                                                     reply_markup=buttons_for_the_second_q())
        db.set_temp_users_message_id(call.from_user.id, message_with_q.message_id)

    if 'second' in call.data:
        user = call.from_user.id
        user_id = str(user)
        
        # Логируем все данные второй анкеты в сессию
        second_q_data = db.get_users_second_q(user)
        if second_q_data:
            db.update_logging_session_sex(user_id, second_q_data[1])  # пол (индекс 1)
            db.update_logging_session_age(user_id, second_q_data[2])  # возраст (индекс 2)
            db.update_logging_session_dish_style(user_id, second_q_data[3])  # стиль питания (индекс 3)
            db.update_logging_session_ccal(user_id, second_q_data[4])  # калории (индекс 4)
            db.update_logging_session_dislike(user_id, second_q_data[5])  # нелюбимые продукты (индекс 5)
            db.update_logging_session_like(user_id, second_q_data[6])  # любимые продукты (индекс 6)
        
        list_of_dishes = []
        recommendation = generate_recommendation(user)
        db.set_temp_rec(user, f"{recommendation}")
        recommendation_text = f"<b>🔝 В ресторане «KoreanChick» нейросеть food2mood рекомендует тебе:</b>\n\n"
        recommendation = eval(db.get_temp_rec(user))
        db.set_temp_rec(user, f"{recommendation}")
        for dish in recommendation:
            recommendation_text += f"{dish[0]} <i>{dish[1]}</i>\n"
            list_of_dishes.append(dish[1])
        recommendation_text += (
            "\n<blockquote>Нажми <b>Ознакомиться с меню</b> 🧾, чтобы поменять рекимендации и детальнее изучить блюда! 👀</blockquote>")

        await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text=recommendation_text,
                                    reply_markup=create_buttons_to_menu(user))
        try:
            await bot.delete_message(chat_id=user, message_id=db.get_first_message_to_delete(user))
        except Exception as e:
            pass
    if 'qr' in call.data:
        user = call.from_user.id
        list_of_dishes = []
        recommendation = generate_recommendation(user)
        db.set_temp_rec(user, f"{recommendation}")
        recommendation_text = f"<b>🔝 В ресторане «KoreanChick» нейросеть food2mood рекомендует тебе:</b>\n\n"
        recommendation = eval(db.get_temp_rec(user))
        db.set_temp_rec(user, f"{recommendation}")
        for dish in recommendation:
            recommendation_text += f"{dish[0]} <i>{dish[1]}</i>\n"
            list_of_dishes.append(dish[1])
        recommendation_text += (
            "\n<blockquote>Нажми <b>Ознакомиться с меню</b> 🧾, чтобы поменять рекимендации и детальнее изучить блюда! 👀</blockquote>")

        await bot.delete_message(chat_id=user, message_id=call.message.message_id)
        await bot.send_message(chat_id=user, text=recommendation_text, reply_markup=create_buttons_to_menu(user))



@dp.callback_query_handler(text_contains='change_the_')
async def change_the_questionnaire(call: types.CallbackQuery):
    await call.answer()
    if 'first' in call.data or 'returnf' in call.data:
        text = 'Выбери свое настроение'
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                    reply_markup=create_mood_buttons())
    if 'second' in call.data:
        user = call.from_user.id
        text = f"▶ Вопрос 1/5:\n\n"
        f"<b>Выбери свой пол:</b>"
        await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text=text,
                                    reply_markup=create_sex_buttons())


@dp.callback_query_handler(text_contains='food_choose_get_')
async def choose_the_mood(call: types.CallbackQuery):
    await call.answer()
    if 'return' not in call.data:
        mood = call.data.split('_')[-1]
        db.set_temp_users_mood(call.from_user.id, mood)
        # Логируем настроение в сессии
        db.update_logging_session_mood(str(call.from_user.id), mood)
    text = 'Выберите степень вашего голода'
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                reply_markup=create_hungry_buttons())


@dp.callback_query_handler(text_contains='choose_hungry')
async def choose_hungry(call: types.CallbackQuery):
    await call.answer()
    hungry_level = call.data.split('_')[-1]
    db.set_temp_users_hungry(call.from_user.id, hungry_level)
    # Логируем уровень голода в сессии
    db.update_logging_session_hungry(str(call.from_user.id), hungry_level)
    text = 'Хочется ли чего-то нового?'
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                reply_markup=create_prefers_buttons())


@dp.callback_query_handler(text_contains='choose_prefers')
async def choose_prefers(call: types.CallbackQuery):
    await call.answer()
    prefer = call.data.split('_')[-1]
    db.set_temp_users_prefers(call.from_user.id, prefer)
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=make_the_second_q(call.from_user.id), reply_markup=buttons_for_the_second_q())


@dp.callback_query_handler(text_contains='choose_sex')
async def choose_sex(call: types.CallbackQuery):
    await call.answer()
    if 'return' not in call.data:
        sex = call.data.split('_')[-1]
        db.set_temp_users_sex(call.from_user.id, sex)
        # Логируем пол в сессии
        db.update_logging_session_sex(str(call.from_user.id), sex)
    text = f"▶ Вопрос 2/5:\n\n<b>Выбери свой возраст:</b>"
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text=text,
                                reply_markup=create_age_buttons(call.from_user.id))


@dp.callback_query_handler(text_contains='choose_age')
async def choose_age(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    age = {'18': 'До 18',
           '25': '18-25',
           '35': '26-35',
           '45': '36-45',
           "45+": "45+"}
    if 'return' not in call.data:
        age = age[call.data.split('_')[-1]]
        db.set_temp_users_age(user, age)
        # Логируем возраст в сессии
        db.update_logging_session_age(str(user), age)
    text = f"▶ Вопрос 3/5:\n\n<b>Какой стиль питания ты предпочитаешь?</b>"
    await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text=text,
                                reply_markup=create_style_buttons())


@dp.callback_query_handler(text_contains='choose_style')
async def choose_style(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    if 'return' not in call.data:
        style = call.data.split('_')[-1]
        db.set_temp_users_food_style(user, style)
        # Логируем стиль питания в сессии
        db.update_logging_session_style(str(user), style)
        if style == 'Диетическое':
            text = f"▶ Вопрос 4/6:\n\n<b>Калораж каждого блюда?</b>"
            await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text=text, reply_markup=create_ccal_buttons())
        else:
            db.set_temp_users_ccal(user, None)
            # Логируем отсутствие калорий в сессии
            db.update_logging_session_ccal(str(user), None)
            text = f"▶ Вопрос 4/5:\n\n<b>Что ты не ешь?</b>\n\n<i>Напиши продукты, которые ты не ешь, одним сообщением в чат, через запятую. <u>Например: лук, чеснок </u></i>"
            db.set_temp_users_state(user, 'dont_like_to_eat')
            message_obj = await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text=text, reply_markup=skip_blacklist(), parse_mode="HTML")
            db.set_temp_users_message_id(user, message_obj.message_id)


@dp.callback_query_handler(text_contains='choose_ccal')
async def choose_ccal(call: types.CallbackQuery):
    await call.answer()
    ccal = call.data.split('_')[-1]
    user = call.from_user.id
    db.set_temp_users_ccal(user, ccal)
    # Логируем калории в сессии
    db.update_logging_session_ccal(str(user), ccal)
    text = f"▶ Вопрос 5/6:\n\n<b>Что ты не ешь?</b>\n\n<i>Напиши продукты, которые ты не ешь, одним сообщением в чат, через запятую. <u>Например: лук, чеснок </u> </i>"
    db.set_temp_users_state(user, 'dont_like_to_eat')
    await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text = text, reply_markup=skip_blacklist())


@dp.callback_query_handler(text_contains='blacklist')
async def blacklist(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    if 'yes' in call.data:
        if db.get_users_second_q(user)[4] is None:
            k = 0
        else:
            k = 1
        text = f"▶ Вопрос {5+k}/{5+k}:\n\n<b>А что ты предпочитаешь из продуктов?</b>\n\n<i>Напишите ответ одним сообщением в чат, через запятую. Искусственный интеллект food2mood проанализирует запрос 😉✌️Например: <u>курица, баклажаны </u> </i>"
        message_obj = await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text=text, reply_markup=skip_whitelist())
        db.set_temp_users_state(user, 'like_to_eat')
        db.set_temp_users_message_id(user, message_obj.message_id)
    if 'no' in call.data:
        if db.get_users_second_q(user)[4] is None:
            k = 0
        else:
            k = 1
        text = f"▶ Вопрос {4+k}/{5+k}:\n\n<b>Что ты не ешь?</b>\n\n<i>Напиши продукты, которые ты не ешь, одним сообщением в чат, через запятую. <u>Например: лук, чеснок </u></i>"
        db.set_temp_users_state(user, 'dont_like_to_eat')
        message_obj = await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text=text, reply_markup=skip_blacklist(),
                                                  parse_mode="HTML")
        db.set_temp_users_message_id(user, message_obj.message_id)


@dp.callback_query_handler(text_contains='whitelist')
async def whitelist(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    if 'yes' in call.data:
        list_of_dishes = []
        recommendation = generate_recommendation(user)
        db.set_temp_rec(user, f"{recommendation}")
        recommendation_text = f"<b>🔝 В ресторане «KoreanChick» нейросеть food2mood рекомендует тебе:</b>\n\n"
        recommendation = eval(db.get_temp_rec(user))
        db.set_temp_rec(user, f"{recommendation}")
        for dish in recommendation:
            recommendation_text += f"{dish[0]} <i>{dish[1]}</i>\n"
            list_of_dishes.append(dish[1])
        recommendation_text += (
            "\n<blockquote>Нажми <b>Ознакомиться с меню</b> 🧾, чтобы поменять рекомендации и детальнее изучить блюда! 👀</blockquote>")
        try:
            await bot.delete_message(chat_id=user, message_id=db.get_first_message_to_delete(user))
        except Exception as e:
            print(e)
        await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text=recommendation_text, reply_markup=create_buttons_to_menu(user))
    if 'no' in call.data:
        if db.get_users_second_q(user)[4] is None:
            k = 0
        else:
            k = 1
        text = f"▶ Вопрос {5 + k}/{5 + k}:\n\n<b>А что ты предпочитаешь из продуктов?</b>\n\n<i>Напишите ответ одним сообщением в чат, через запятую. Искусственный интеллект food2mood проанализирует запрос 😉✌️️Например: <u>курица, баклажаны </u></i>"
        message_obj = await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text=text, reply_markup=skip_whitelist())
        db.set_temp_users_state(user, 'like_to_eat')
        db.set_temp_users_message_id(user, message_obj.message_id)


@dp.callback_query_handler(text_contains='skip')
async def skip(call: types.CallbackQuery):
    await call.answer()
    user = call.from_user.id
    if 'blaclist' in call.data:
        if db.get_users_second_q(user)[4] is None:
            k = 0
        else:
            k = 1
        text = f"▶ Вопрос {5 + k}/{5 + k}:\n\n<b>А что ты предпочитаешь из продуктов?</b>\n\n<i>Напишите ответ одним сообщением в чат, через запятую. Искусственный интеллект food2mood проанализирует запрос 😉✌️Например: <u>курица, баклажаны </u> </i>"
        message_obj = await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text=text, reply_markup=skip_whitelist())
        db.set_temp_users_state(user, 'like_to_eat')
        db.set_temp_users_message_id(user, message_obj.message_id)
    else:
        list_of_dishes = []
        recommendation = generate_recommendation(user)
        db.set_temp_rec(user, f"{recommendation}")
        recommendation_text = f"<b>🔝 В ресторане «KoreanChick» нейросеть food2mood рекомендует тебе:</b>\n\n"
        recommendation = eval(db.get_temp_rec(user))
        db.set_temp_rec(user, f"{recommendation}")
        for dish in recommendation:
            recommendation_text += f"{dish[0]} <i>{dish[1]}</i>\n"
            list_of_dishes.append(dish[1])
        recommendation_text += (
            "\n<blockquote>Нажми <b>Ознакомиться с меню</b> 🧾, чтобы поменять рекомендации и детальнее изучить блюда! 👀</blockquote>")
        try:
            await bot.delete_message(chat_id=user, message_id=db.get_first_message_to_delete(user))
        except Exception as e:
            print(e)
        await bot.edit_message_text(chat_id=user, message_id=call.message.message_id, text=recommendation_text,
                                    reply_markup=create_buttons_to_menu(user))
# ======================================================================================================================
# ===== Создание клавиатур =================================================================================================
# ======================================================================================================================


def create_mood_buttons():
    menu = InlineKeyboardMarkup(row_width=3)

    btn1 = InlineKeyboardButton(text=f"Радость {icons['Радость']}",
                                callback_data="food_choose_get_Радость")

    btn2 = InlineKeyboardButton(text=f"Печаль {icons['Печаль']}",
                                callback_data="food_choose_get_Печаль")

    btn3 = InlineKeyboardButton(text=f"Гнев {icons['Гнев']}",
                                callback_data="food_choose_get_Гнев")

    btn4 = InlineKeyboardButton(text=f"Спокойствие {icons['Спокойствие']}",
                                callback_data="food_choose_get_Спокойствие")

    btn5 = InlineKeyboardButton(text=f"Волнение {icons['Волнение']}",
                                callback_data="food_choose_get_Волнение")

    btn9 = InlineKeyboardButton(text="⬅️ Назад",
                                callback_data="order_at_rest")

    menu.add(btn1, btn2, btn3)
    menu.add(btn4, btn5)
    menu.add(btn9)

    return menu


def create_hungry_buttons():
    menu = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text=f"2/10",
                                callback_data="choose_hungry_2")

    btn2 = InlineKeyboardButton(text=f"5/10",
                                callback_data="choose_hungry_5")

    btn3 = InlineKeyboardButton(text=f"7/10",
                                callback_data="choose_hungry_7")

    btn4 = InlineKeyboardButton(text=f"10/10",
                                callback_data="choose_hungry_10")

    btn9 = InlineKeyboardButton(text="⬅️ Назад",
                                callback_data="change_the_returnf")

    menu.add(btn1, btn2)
    menu.add(btn3, btn4)
    menu.add(btn9)
    return menu


def create_prefers_buttons():
    menu = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text=f"Мне как обычно 👌",
                                callback_data="choose_prefers_Мне как обычно")

    btn2 = InlineKeyboardButton(text=f"Хочу экспериментов 🆕",
                                callback_data="choose_prefers_Хочу экспериментов")

    btn9 = InlineKeyboardButton(text="⬅️ Назад",
                                callback_data="food_choose_get_return")

    menu.add(btn1, btn2)
    menu.add(btn9)
    return menu


def create_sex_buttons():
    menu = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton(text=f"Мужчина {icons['Мужчина']}",
                                callback_data="choose_sex_Мужчина")

    btn2 = InlineKeyboardButton(text=f"Женщина {icons['Женщина']}",
                                callback_data="choose_sex_Женщина")

    btn9 = InlineKeyboardButton(text="⬅️ Назад",
                                callback_data="confirmation_of_the_first_q")

    menu.add(btn1, btn2)
    menu.add(btn9)
    return menu


def create_age_buttons(user):
    sex = db.get_users_second_q(user)[1]
    if sex == "Мужчина":
        age_emoji = ["🧒", "🧑", "👨‍🦱", "🧔‍♂️", "👨‍🦳"]
    else:
        age_emoji = ["👧", "👩", "👱‍♀️", "👩‍🦱", "🧓"]
    menu = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton(text=f"До 18 {age_emoji[0]}",
                                callback_data="choose_age_18")

    btn2 = InlineKeyboardButton(text=f"18-25 {age_emoji[1]}",
                                callback_data="choose_age_25")

    btn3 = InlineKeyboardButton(text=f"26-35 {age_emoji[2]}",
                                callback_data="choose_age_35")

    btn4 = InlineKeyboardButton(text=f"36-45 {age_emoji[3]}",
                                callback_data="choose_age_45")

    btn5 = InlineKeyboardButton(text=f"45+ {age_emoji[4]}",
                                callback_data="choose_age_45+")

    menu.row(btn1)
    menu.row(btn2, btn3, btn4)
    menu.row(btn5)

    btn9 = InlineKeyboardButton(text="⬅️ Назад",
                                callback_data="change_the_second_q")

    menu.add(btn9)
    return menu


def create_style_buttons():
    menu = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton(text="Стандартное 🥘",
                                callback_data="choose_style_Стандартное")

    btn2 = InlineKeyboardButton(text="Диетическое 🥗",
                                callback_data="choose_style_Диетическое")

    menu.row(btn1, btn2)

    back_btn = InlineKeyboardButton(text="⬅️ Назад",
                                    callback_data="choose_sex_return")
    menu.add(back_btn)
    return menu

def create_ccal_buttons():
    menu = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton(text="<300",
                                callback_data="choose_ccal_300")

    btn2 = InlineKeyboardButton(text="<500",
                                callback_data="choose_ccal_500")

    btn3 = InlineKeyboardButton(text="<700",
                                callback_data="choose_ccal_700")
    menu.row(btn1, btn2, btn3)

    back_btn = InlineKeyboardButton(text="⬅️ Назад",
                                    callback_data="choose_age_return")
    menu.add(back_btn)
    return menu


def skip_blacklist():
    menu = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton(text="Пропустить ❌",
                                callback_data="skip_blaclist")
    menu.add(btn1)
    return menu


def skip_whitelist():
    menu = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton(text="Пропустить ❌",
                                callback_data="skip_whitlist")
    menu.add(btn1)
    return menu