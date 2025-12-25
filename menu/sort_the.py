import re
from config import dp, bot, db
import difflib
import json
import random
import pandas as pd
from files.icons import icons


def read_table(user, category: str, mood: str, style: str, rec: str,
               blacklist: list, whitelist: list, numb: int, price: int, g: int, first_dish_name: str or None):
    # Загружаем таблицу с меню
    df = pd.DataFrame(db.menu_get(), columns=[
        'id',
        'Категория',
        'Название блюда',
        'Комментарий нейросети',
        'Ингредиенты',
        'Простые ингредиенты',
        'КБЖУ',
        'Граммы',
        'Цена',
        'Размер',
        'iiko_id',
        'Стиль питания',
        'Настроение',
        'Рекомендации нутрициолога',
        'Ссылка',
        'Дополнительные продажи',
        'Рейтинг',
        'Отзывы',
        'Коины'
    ])
    # Получаем рейтинги пользователя
    user_ratings = {}
    try:
        result = db.cursor.execute("SELECT users_dish_coefficients FROM correlation_coefficient WHERE user_id = ?",
                                   (user,)).fetchone()
        if result and result[0]:
            user_ratings = eval(result[0])
    except Exception as e:
        print(f"Error getting user ratings: {e}")
    df = df[df['Настроение'].str.contains(mood)]
    df = df.loc[df['Категория'] == category]
    df = df.values.tolist()

    if not len(df):
        return None, None, None

    rec_mood = {
        'Радость': 0,
        'Печаль': 1,
        'Гнев': 2,
        'Спокойствие': 3,
        'Волнение': 4,
    }

    rec_item = 0
    if rec == 'Нутрициолог' and (df[0][9] != 'None' or df[0][9] != '' or df[0][9] is not None):
        rec_item = 13
    if rec == 'Пользователи' and (df[0][10] != 'None' or df[0][10] != '' or df[0][10] is not None):
        rec_item = 10
    if rec == 'Обломов' and (df[0][11] != 'None' or df[0][11] != '' or df[0][11] is not None):
        rec_item = 11
    if rec == 'Ивлев' and (df[0][12] != 'None' or df[0][12] != '' or df[0][12] is not None):
        rec_item = 12

    if rec_item == 0:
        return None, None, None

    def sort_by(item):
        # Получаем базовый порядок из рекомендаций
        mood_info = item[rec_item].split(', ')

        min_order = float('inf')
        base_order_found = False
        for info in mood_info:
            match = re.match(r'(\w+)\s*=\s*(\d+)', info)
            if match:
                mood_name, mood_order = match.groups()
                if mood_name.strip() == mood:
                    min_order = min(min_order, int(mood_order))
                    base_order_found = True

        # Учитываем рейтинг пользователя с корректировкой позиций
        dish_id = str(item[0])
        dish_name = str(item[2])
        debug_base_order = min_order if base_order_found else 'inf'
        debug_user_rating = None
        debug_rating_count = None
        debug_position_correction = 0
        
        if dish_id in user_ratings:
            rating_data = user_ratings[dish_id]
            if isinstance(rating_data, dict):
                user_rating = rating_data['rating']
                rating_count = rating_data['count']
                debug_user_rating = user_rating
                debug_rating_count = rating_count
            else:
                user_rating = float(rating_data)
                debug_user_rating = user_rating
                debug_rating_count = 1
            
            # Применяем корректировки позиций по рейтингу
            if user_rating == 5:  # Поднимаем на 2 позиции вверх
                debug_position_correction = -3
            elif user_rating == 4:  # Поднимаем на 1 позицию вверх
                debug_position_correction = -2
            elif user_rating == 3:  # Остается на месте
                debug_position_correction = 1
            elif user_rating == 2:  # Опускаем на 1 позицию вниз
                debug_position_correction = 2
            elif user_rating == 1:  # Опускаем на 2 позиции вниз
                debug_position_correction = 3
            
            # Добавляем корректировку к базовому порядку
            min_order = min_order + debug_position_correction

        try:
            print(f"[SORT_DEBUG] mood={mood} rec={rec} rec_item={rec_item} id={dish_id} name={dish_name} base={debug_base_order} user_rating={debug_user_rating} count={debug_rating_count} pos_correction={debug_position_correction} result={min_order}")
        except Exception:
            pass

        return min_order

    # Изменение в сортировке, передача rec_item в sort_by функцию
    ccal_user = db.get_temp_users_ccal(user)
    df2 = []
    if ccal_user is not None and ccal_user != 'пусто':
        for e in df:
            dish_ccal = float(e[6].split('Кк')[1]) * (float(e[7]) / 100)
            if e[6] is not None:
                if float(db.get_temp_users_ccal(user)) > float(dish_ccal) != 0:
                    df2.append(e)
    else:
        df2 = df
    # Добавляем вторичный ключ сортировки для стабильного порядка
    # Используем название блюда как третий ключ для гарантии стабильного порядка
    df_new = sorted(df2, key=lambda x: (sort_by(x), x[0], x[2]))  # x[2] - название блюда

    # Диагностика: показываем первые 10 элементов после сортировки с их ключами
    try:
        preview = []
        for item in df_new[:10]:
            try:
                preview.append({
                    'id': item[0],
                    'name': item[2],
                    'sort_key': sort_by(item)
                })
            except Exception:
                continue
        print(f"[SORT_DEBUG] TOP_AFTER_SORT (first 10): {preview}")
    except Exception:
        pass
    dishes = []
    dishes_white = []
    try:
        stop_list = list(eval(db.get_stop_list(db.get_client_temp_rest(user))).keys())
    except Exception as e:
        stop_list = []
    if first_dish_name:
        first_dish = db.restaurants_get_by_name(first_dish_name)
        dish_ingredients_unformatted = str(first_dish[5]).strip().lower()
        dish_ingredients = dish_ingredients_unformatted.split(',')
        dishes_white.append({
            "Категория": first_dish[1],
            "Название": first_dish[2],
            "Описание": first_dish[3],
            "Ингредиенты": dish_ingredients,
            "Стиль питания": first_dish[11],
            "Настроение": mood,
            "Ссылка": first_dish[13],
            "Рейтинг": first_dish[16],
            "Цена": first_dish[8],
            "Грамм": first_dish[7],
            "Размер": first_dish[9],
            "КБЖУ": first_dish[6]
        })
    for dish in df_new:
        dish_ingredients = [ingredient.strip() for ingredient in str(dish[5]).lower().split(',')]
        if set(blacklist) & set(dish_ingredients):
            continue

        if dish[2] == first_dish_name or dish[2] in stop_list:
            continue

        dish_data = {
            "Категория": dish[1],
            "Название": dish[2],
            "Описание": dish[3],
            "Ингредиенты": dish_ingredients,
            "Стиль питания": dish[11],
            "Настроение": mood,
            "Ссылка": dish[13],
            "Рейтинг": dish[16],
            "Цена": dish[8],
            "Грамм": dish[7],
            "Размер": dish[9],
            "КБЖУ": dish[6]
        }

        # Добавляем информацию о рейтинге пользователя
        dish_id = str(dish[0])
        if dish_id in user_ratings:
            rating_data = user_ratings[dish_id]
            if isinstance(rating_data, dict):
                dish_data["user_rating"] = rating_data['rating']
                dish_data["rating_count"] = rating_data['count']
            else:
                dish_data["user_rating"] = float(rating_data)
                dish_data["rating_count"] = 1

        if set(whitelist) & set(dish_ingredients):
            dishes_white.append(dish_data)
        else:
            dishes.append(dish_data)

    # Формируем итоговый список с сохранением порядка сортировки
    # Сначала добавляем все блюда в правильном порядке сортировки
    all_dishes = []
    print(f"[SORT_DEBUG] Processing df_new with {len(df_new)} dishes")
    for i, dish in enumerate(df_new):
        dish_name = dish[2]
        print(f"[SORT_DEBUG] Processing dish {i}: {dish_name}")
        
        dish_ingredients = [ingredient.strip() for ingredient in str(dish[5]).lower().split(',')]
        if set(blacklist) & set(dish_ingredients):
            print(f"[SORT_DEBUG] Skipping {dish_name} - blacklisted ingredients")
            continue
        if dish[2] == first_dish_name or dish[2] in stop_list:
            print(f"[SORT_DEBUG] Skipping {dish_name} - first_dish or stop_list")
            continue
        
        # Ищем это блюдо в dishes_white или dishes
        found_dish = None
        
        # Сначала проверяем dishes_white
        for w_dish in dishes_white:
            if w_dish["Название"] == dish_name:
                found_dish = w_dish
                print(f"[SORT_DEBUG] Found {dish_name} in dishes_white")
                break
        
        # Если не найдено в white, ищем в обычных dishes
        if not found_dish:
            for d_dish in dishes:
                if d_dish["Название"] == dish_name:
                    found_dish = d_dish
                    print(f"[SORT_DEBUG] Found {dish_name} in dishes")
                    break
        
        if found_dish:
            all_dishes.append(found_dish)
            print(f"[SORT_DEBUG] Added {dish_name} to all_dishes")
        else:
            print(f"[SORT_DEBUG] NOT FOUND {dish_name} in dishes_white or dishes!")
    
    # Добавляем first_dish в начало, если он есть и у него нет негативного рейтинга
    if first_dish_name:
        print(f"[SORT_DEBUG] FIRST_DISH_NAME: {first_dish_name}")
        first_dish_data = None
        for w_dish in dishes_white:
            if w_dish["Название"] == first_dish_name:
                first_dish_data = w_dish
                break
        
        if first_dish_data:
            # Проверяем рейтинг first_dish из user_ratings
            should_insert_at_beginning = True
            # Получаем ID блюда по названию
            try:
                first_dish_id = str(db.restaurants_get_dish(first_dish_name)[0])
            except:
                first_dish_id = ""
            
            if first_dish_id in user_ratings:
                rating_data = user_ratings[first_dish_id]
                if isinstance(rating_data, dict):
                    rating = rating_data['rating']
                else:
                    rating = float(rating_data)
                
                if rating <= 2:  # Если рейтинг 1 или 2, не вставляем в начало
                    should_insert_at_beginning = False
                    print(f"[SORT_DEBUG] FIRST_DISH has negative rating {rating}, keeping in sorted order")
            
            if should_insert_at_beginning:
                print(f"[SORT_DEBUG] INSERTING FIRST_DISH at position 0: {first_dish_data['Название']}")
                all_dishes.insert(0, first_dish_data)
            else:
                print(f"[SORT_DEBUG] FIRST_DISH already in sorted position: {first_dish_data['Название']}")
                # Убеждаемся, что first_dish есть в списке (он должен быть добавлен в основном цикле)
                dish_found_in_list = False
                for dish in all_dishes:
                    if dish["Название"] == first_dish_name:
                        dish_found_in_list = True
                        break
                
                if not dish_found_in_list:
                    print(f"[SORT_DEBUG] FIRST_DISH not found in list, finding correct position")
                    # Находим правильную позицию для first_dish согласно сортировке
                    first_dish_key = None
                    for dish in df_new:
                        if dish[2] == first_dish_name:
                            first_dish_key = sort_by(dish)
                            break
                    
                    if first_dish_key is not None:
                        # Вставляем в правильную позицию согласно ключу сортировки
                        insert_position = 0
                        for i, dish in enumerate(all_dishes):
                            dish_name = dish["Название"]
                            # Находим соответствующий элемент в df_new для получения ключа
                            for df_dish in df_new:
                                if df_dish[2] == dish_name:
                                    dish_key = sort_by(df_dish)
                                    if dish_key > first_dish_key:
                                        insert_position = i
                                        break
                                    break
                            if insert_position > 0:
                                break
                        
                        print(f"[SORT_DEBUG] Inserting FIRST_DISH at position {insert_position}")
                        all_dishes.insert(insert_position, first_dish_data)
                    else:
                        print(f"[SORT_DEBUG] Could not find sort key for FIRST_DISH, adding to end")
                        all_dishes.append(first_dish_data)

    # Возвращаем результат
    if len(all_dishes) > 0:
        try:
            ordered_names = [d["Название"] for d in all_dishes[:20]]
            print(f"[SORT_DEBUG] ORDERED_NAMES (first 20): {ordered_names}")
        except Exception:
            pass
        if len(all_dishes) > numb:
            try:
                print(f"[SORT_DEBUG] SELECTED: numb={numb} name={all_dishes[numb]['Название']} len={len(all_dishes)} remaining={len(all_dishes) - numb - 1}")
            except Exception:
                pass
            return all_dishes[numb], len(all_dishes), len(all_dishes) - numb - 1
        else:
            try:
                print(f"[SORT_DEBUG] SELECTED: numb={numb} clamped_to_last name={all_dishes[-1]['Название']} len={len(all_dishes)} remaining=0")
            except Exception:
                pass
            return all_dishes[-1], len(all_dishes), 0
    else:
        return None, None, None


def read_table_simple(user, category: str, numb: int, price: int, g: int):
    """Упрощенная версия read_table без фильтрации по настроению и рекомендациям"""
    # Загружаем таблицу с меню
    df = pd.DataFrame(db.menu_get(), columns=[
        'id',
        'Категория',
        'Название блюда',
        'Комментарий нейросети',
        'Ингредиенты',
        'Простые ингредиенты',
        'КБЖУ',
        'Граммы',
        'Цена',
        'Размер',
        'iiko_id',
        'Стиль питания',
        'Настроение',
        'Рекомендации нутрициолога',
        'Ссылка',
        'Дополнительные продажи',
        'Рейтинг',
        'Отзывы',
        'Коины'
    ])
    
    # Фильтруем только по категории
    df = df.loc[df['Категория'] == category]
    df = df.values.tolist()

    if not len(df):
        return None, None, None

    # Получаем рейтинги пользователя
    user_ratings = {}
    try:
        result = db.cursor.execute("SELECT users_dish_coefficients FROM correlation_coefficient WHERE user_id = ?",
                                   (user,)).fetchone()
        if result and result[0]:
            user_ratings = eval(result[0])
    except Exception as e:
        print(f"Error getting user ratings: {e}")

    # Получаем стоп-лист
    try:
        stop_list = list(eval(db.get_stop_list(db.get_client_temp_rest(user))).keys())
    except Exception as e:
        stop_list = []

    # Простая сортировка по ID (можно изменить на другую логику)
    df_sorted = sorted(df, key=lambda x: x[0])

    # Формируем список блюд
    all_dishes = []
    for dish in df_sorted:
        if dish[2] in stop_list:
            continue

        dish_data = {
            "Категория": dish[1],
            "Название": dish[2],
            "Описание": dish[3],
            "Ингредиенты": [ingredient.strip() for ingredient in str(dish[5]).lower().split(',')],
            "Стиль питания": dish[11],
            "Настроение": dish[12],
            "Ссылка": dish[14],
            "Рейтинг": dish[16],
            "Цена": dish[8],
            "Грамм": dish[7],
            "Размер": dish[9],
            "КБЖУ": dish[6]
        }

        # Добавляем информацию о рейтинге пользователя
        dish_id = str(dish[0])
        if dish_id in user_ratings:
            rating_data = user_ratings[dish_id]
            if isinstance(rating_data, dict):
                dish_data["user_rating"] = rating_data['rating']
                dish_data["rating_count"] = rating_data['count']
            else:
                dish_data["user_rating"] = float(rating_data)
                dish_data["rating_count"] = 1

        all_dishes.append(dish_data)

    # Возвращаем результат
    if len(all_dishes) > 0:
        if len(all_dishes) > numb:
            return all_dishes[numb], len(all_dishes), len(all_dishes) - numb - 1
        else:
            return all_dishes[-1], len(all_dishes), 0
    else:
        return None, None, None


def get_dish(user: int):
    """Упрощенная версия get_dish без фильтрации по настроению и рекомендациям"""
    category = db.get_temp_users_category(user)
    numb = db.get_client_temp_dish(user)
    price = db.get_dish_price(user)
    g = db.get_g(user)
    return read_table_simple(user, category, numb, price, g)


def generate_recommendation(user):
    mood = db.get_temp_users_mood(user)
    style = db.get_temp_users_style(user)
    blacklist = [ingredient.strip() for ingredient in db.get_temp_users_dont_like_to_eat(user).split(",")]
    whitelist = [ingredient.strip() for ingredient in db.get_temp_users_like_to_eat(user).split(",")]

    # Получаем оценки пользователя
    user_ratings = {}
    try:
        result = db.cursor.execute("SELECT users_dish_coefficients FROM correlation_coefficient WHERE user_id = ?",
                                   (user,)).fetchone()
        if result and result[0]:
            user_ratings = eval(result[0])
    except Exception as e:
        print(f"Error getting user ratings: {e}")

    # Загружаем таблицу с меню
    df = pd.DataFrame(db.menu_get(), columns=[
        'id',
        'Категория',
        'Название блюда',
        'Комментарий нейросети',
        'Ингредиенты',
        'Простые ингредиенты',
        'КБЖУ',
        'Граммы',
        'Цена',
        'Размер',
        'iiko_id',
        'Стиль питания',
        'Настроение',
        'Рекомендации нутрициолога',
        'Ссылка',
        'Дополнительные продажи',
        'Рейтинг',
        'Отзывы',
        'Коины'
    ])
    df = df[df['Настроение'].str.contains(mood)]
    df = df[df['Стиль питания'].str.contains(style)]
    if df.empty:
        return None

    # Получаем стоп-лист
    try:
        stop_list = list(eval(db.get_stop_list(db.get_client_temp_rest(user))).keys())
    except Exception as e:
        stop_list = []

    # Функция для сортировки блюд по рейтингу (как в read_table)
    def sort_by_rating(dish_data):
        # Находим оригинальные данные блюда из DataFrame
        original_dish = None
        for dish in df.values.tolist():
            if str(dish[0]) == str(dish_data['id']):
                original_dish = dish
                break

        if not original_dish:
            return 0

        # Получаем базовый порядок из рекомендаций нутрициолога
        mood_info = original_dish[13].split(', ')  # Рекомендации нутрициолога

        min_order = float('inf')
        for info in mood_info:
            match = re.match(r'(\w+)\s*=\s*(\d+)', info)
            if match:
                mood_name, mood_order = match.groups()
                if mood_name.strip() == mood:
                    min_order = min(min_order, int(mood_order))

        # Учитываем рейтинг пользователя
        dish_id = str(dish_data['id'])
        if dish_id in user_ratings:
            rating_data = user_ratings[dish_id]
            if isinstance(rating_data, dict):
                user_rating = rating_data['rating']
                rating_count = rating_data['count']
                min_order = min_order - (user_rating * 10 * (1 + rating_count / 10))
            else:
                user_rating = float(rating_data)
                min_order = min_order - (user_rating * 10)

        return min_order

    # Группируем блюда по категориям и фильтруем
    category_dishes = {}
    banned_categories = ["Хлеб", "Соус"]

    for dish in df.values.tolist():
        category = dish[1]

        # Пропускаем запрещённые категории
        if category in banned_categories:
            continue

        # Проверяем ингредиенты
        dish_ingredients = [ingredient.strip() for ingredient in str(dish[4]).lower().split(',')]
        if set(blacklist) & set(dish_ingredients):
            continue

        # Проверяем стоп-лист
        if dish[2] in stop_list:
            continue

        # Проверяем, что категория есть в иконках
        if category not in icons:
            continue

        dish_data = {
            "Категория": category,
            "Название": dish[2],
            "Цена": dish[8],
            "Размер": dish[9],
            "id": dish[0],
            "Ингредиенты": dish_ingredients
        }

        # Добавляем информацию о рейтинге пользователя
        dish_id = str(dish[0])
        if dish_id in user_ratings:
            dish_data["user_rating"] = user_ratings[dish_id]

        # Разделяем на whitelist и обычные блюда
        if set(whitelist) & set(dish_ingredients):
            if category not in category_dishes:
                category_dishes[category] = {"white": [], "regular": []}
            category_dishes[category]["white"].append(dish_data)
        else:
            if category not in category_dishes:
                category_dishes[category] = {"white": [], "regular": []}
            category_dishes[category]["regular"].append(dish_data)

    # Выбираем предпочтительные категории или случайные, если предпочтительных нет
    available_categories = list(category_dishes.keys())
    if len(available_categories) == 0:
        return None

    # Получаем предпочтительные категории
    prefer_categories = db.get_prefer_categories()

    # Фильтруем только те предпочтительные категории, которые доступны
    available_prefer_categories = [cat for cat in prefer_categories if cat in available_categories]

    if len(available_prefer_categories) >= 5:
        # Если предпочтительных категорий достаточно, берём первые 5
        selected_categories = available_prefer_categories[:5]
    elif len(available_prefer_categories) > 0:
        # Если предпочтительных категорий меньше 5, дополняем случайными
        remaining_categories = [cat for cat in available_categories if cat not in available_prefer_categories]
        needed_random = 5 - len(available_prefer_categories)
        random_categories = random.sample(remaining_categories, min(needed_random, len(remaining_categories)))
        selected_categories = available_prefer_categories + random_categories
    else:
        # Если предпочтительных категорий нет, выбираем случайные
        selected_categories = random.sample(available_categories, min(5, len(available_categories)))

    recommendation = []

    for category in selected_categories:
        # Сначала берём из whitelist, потом из обычных
        dishes_to_choose = category_dishes[category]["white"] + category_dishes[category]["regular"]

        if dishes_to_choose:
            # Сортируем по рейтингу и берём лучшее блюдо
            dishes_to_choose.sort(key=sort_by_rating)
            best_dish = dishes_to_choose[0]

            recommendation.append((
                f"{icons[category]}",
                best_dish["Название"],
                best_dish["Цена"],
                best_dish.get("user_rating", 0)
            ))

    # Сортируем по цене (как было раньше)
    recommendation = sorted(recommendation, key=lambda x: int(x[2]), reverse=True)

    # Применяем корректировки на основе оценок пользователя
    for i in range(len(recommendation)):
        rating = recommendation[i][3]
        if rating == 5:  # Поднимаем на 2 позиции вверх
            if i > 1:
                recommendation[i], recommendation[i - 2] = recommendation[i - 2], recommendation[i]
        elif rating == 4:  # Поднимаем на 1 позицию вверх
            if i > 0:
                recommendation[i], recommendation[i - 1] = recommendation[i - 1], recommendation[i]
        elif rating == 2:  # Опускаем на 1 позицию вниз
            if i < len(recommendation) - 1:
                recommendation[i], recommendation[i + 1] = recommendation[i + 1], recommendation[i]
        elif rating == 1:  # Опускаем на 2 позиции вниз
            if i < len(recommendation) - 2:
                recommendation[i], recommendation[i + 2] = recommendation[i + 2], recommendation[i]

    # Убираем рейтинг из кортежа перед возвратом
    recommendation = [(icon, name, price) for icon, name, price, _ in recommendation]
    return recommendation
