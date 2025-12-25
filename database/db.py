import sqlite3
import datetime
import json
import time

import requests


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

        # Список разрешенных администраторов
        self.allowed_admins = [1456241115]

    def return_connect(self):
        return self.connection

    # ======================================================================================================================
    # ===== ТАБЛИЦА: users =================================================================================================
    # ======================================================================================================================

    # --- Добавить значение ---

    def add_users_user(self, user_id, user_link, user_reg_time, user_name=None, user_first_name=None,
                       user_last_name=None, coin_count=0):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO users (user_id, user_link, user_name, user_first_name, user_last_name, user_reg_time, foodToMoodCoin) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, user_link, user_name, user_first_name, user_last_name, user_reg_time, coin_count))

    def del_users_user(self, user_id):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM users WHERE user_id = ?",
                (user_id,))

    def check_users_user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchall()
            return bool(len(result))

        # --- Ban ---

    def set_users_ban(self, user_id: int, ban: int):
        with self.connection:
            self.cursor.execute("UPDATE users SET ban = ? WHERE user_id = ?", (ban, user_id))

    def get_users_ban(self, user_id) -> dict:
        with self.connection:
            result = self.connection.execute("SELECT ban FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()
            return bool(int(result[0][0]))

        # --- Mode ---

    def set_users_mode(self, user_id: int, mode_id: int, mode_key: str):
        with self.connection:
            self.cursor.execute("UPDATE users SET mode_id = ?, mode_key = ? WHERE user_id = ?",
                                (mode_id, mode_key, user_id))

    def get_users_mode(self, user_id) -> dict:
        with self.connection:
            result = self.connection.execute("SELECT mode_id, mode_key FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()
            return {'id': int(result[0][0]), 'key': str(result[0][1])}

        # --- Message ---

    def set_users_first_message(self, user_id, id):
        with self.connection:
            return self.cursor.execute("UPDATE users SET first_message = ? WHERE user_id = ?", (id, user_id))

    def get_users_first_message(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT first_message FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()
            for row in result:
                id = str(row[0])
                return id
            return 0

    def set_users_last_message(self, user_id, id):
        with self.connection:
            return self.cursor.execute("UPDATE users SET last_message = ? WHERE user_id = ?", (id, user_id))

    def get_users_last_message(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT last_message FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()
            for row in result:
                id = str(row[0])
                return id
            return 0

        # --- User link ---

    def get_users_user_link(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT user_link FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()

            for row in result:
                user_link = str(row[0])
            return user_link

        # --- User name ---

    def get_users_user_name(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT user_name FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()

            for row in result:
                user_name = str(row[0])
            return user_name

        # --- User first name ---

    def get_users_user_first_name(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT user_first_name FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()

            for row in result:
                user_first_name = str(row[0])
            return user_first_name

        # --- User last name ---

    def get_users_user_last_name(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT user_last_name FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()

            for row in result:
                user_last_name = str(row[0])
            return user_last_name

        # --- User reg time ---

    def get_users_user_reg_time(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT user_reg_time FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()

            for row in result:
                user_reg_time = str(row[0])
            return user_reg_time

            # --- User last recommendation time ---

        # def set_users_last_recomendation_time(self, user_id, current_time):
        #             with self.connection:
        #                 return self.cursor.execute(
        #                     "UPDATE users SET last_recomendation_time = ? FROM users WHERE user_id = ?",
        #                     (user_id, current_time))

    def get_users_last_recomendation_time(self, user_id):
        with self.connection:
            result = self.connection.execute("SELECT last_recomendation_time FROM users WHERE user_id = ?",
                                             (user_id,)).fetchall()

        for row in result:
            last_recomendation_time = str(row[0])
            return last_recomendation_time

        # --- Food2Mood Coin

    def add_food_to_mood_coin(self, user_id: int, coin_count: int):
        with self.connection:
            self.cursor.execute("UPDATE users SET foodToMoodCoin = foodToMoodCoin + ? WHERE user_id = ?",
                                (coin_count, user_id))

    def clear_food_to_mood_coin(self, user_id: int):
        with self.connection:
            self.cursor.execute("UPDATE users SET foodToMoodCoin = foodToMoodCoin + ? WHERE user_id = ?", (user_id,))

    def get_users_food_to_mood_coin(self, user_id: int):
        with self.connection:
            result = self.connection.execute("SELECT foodToMoodCoin FROM users WHERE user_id = ?", (user_id,))
            for row in result:
                foodToMoodCoin = str(row[0])
            return foodToMoodCoin

        # --- All users ---

    def get_users_users(self):
        with self.connection:
            result = self.connection.execute("SELECT user_id FROM users").fetchall()
            users_id = []
            for row in result:
                users_id.append(int(row[0]))
            return users_id

    def set_users_phone(self, user, phone):
        with self.connection:
            self.cursor.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user))

    def get_users_phone(self, user):
        with self.connection:
            result = self.cursor.execute(
                "SELECT phone FROM users WHERE user_id = ?",
                (user,)).fetchall()
        try:
            return result[0][0]
        except:
            return None

    # ======================================================================================================================
    # ===== ТАБЛИЦА: menu =================================================================================================
    # ======================================================================================================================
    # --- all categories ---
    # --- all categories ---
    def restaurants_get_dish(self, dish) -> list:
        if type(dish) is list:
            dish = dish[0]
        if '»' in dish:
            dish = dish[1:-1]
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM menu WHERE dish_name = ?",
                (dish,)).fetchall()
            return result[0]

    def get_all_categories(self):
        with self.connection:
            result = self.connection.execute("SELECT dish_category FROM menu").fetchall()
            # Использование множества для удаления дубликатов и преобразование его обратно в список
            unique_categories = list(set(category[0] for category in result))
            return unique_categories

    def restaurants_find_all(self, keyword):
        with self.connection:
            self.connection.execute("DROP TABLE IF EXISTS rest_fts")
            self.connection.execute("CREATE VIRTUAL TABLE rest_fts USING fts4(id, rest_name, rest_address)")
            self.connection.execute("INSERT INTO rest_fts(id, rest_name, rest_address) "
                                    "SELECT id, rest_name, rest_address "
                                    "FROM menu")
            result = self.connection.execute(
                f"SELECT id, rest_name, rest_address FROM rest_fts WHERE rest_name LIKE '%{keyword}%' OR rest_address LIKE '%{keyword}%'").fetchall()
            all_posts = []
            rest = []
            for row in result:
                row = list(row)
                if [row[1], row[2]] not in rest:
                    all_posts.append(row)
                    rest.append([row[1], row[2]])
            return all_posts

    def restaurants_find_address(self, rest_name):
        with self.connection:
            result = self.connection.execute(
                f"SELECT rest_address FROM menu WHERE rest_name LIKE '%{rest_name}%'").fetchone()
            return result[0]

    def restaurants_find_dish(self, rest_name, keyword):
        with self.connection:
            self.connection.execute("DROP TABLE IF EXISTS dish_fts")
            self.connection.execute(
                "CREATE VIRTUAL TABLE dish_fts USING fts4(id, rest_name, rest_address, dish_name)")
            self.connection.execute("INSERT INTO dish_fts(id, rest_name, rest_address, dish_name) "
                                    "SELECT id, rest_name, rest_address, dish_name "
                                    "FROM menu")
            # self.connection.execute(f"SELECT * FROM dish_fts WHERE dish_name LIKE '%{keyword}%'")
            result = self.connection.execute(
                f"SELECT * FROM dish_fts WHERE rest_name = '{rest_name}' AND dish_name LIKE '%{keyword}%'").fetchall()
            return result

    def restaurants_get_all(self):
        with self.connection:
            result = self.connection.execute(
                "SELECT id, rest_name, rest_address FROM menu").fetchall()
            all_posts = []
            rest = []
            for row in result:
                row = list(row)
                if [row[1], row[2]] not in rest:
                    all_posts.append(row)
                    rest.append([row[1], row[2]])
            return all_posts

    def restaurants_get_all_dish(self):
        with self.connection:
            result = self.connection.execute(
                "SELECT id, dish_name FROM menu").fetchall()
            return result

    def menu_get(self) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM menu").fetchall()
            return result

    def get_dish_id(self, restaurant, name) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT id FROM menu WHERE rest_name = ? and dish_name = ?",
                (restaurant, name)).fetchone()[0]
            return result

    def get_dish_price(self, id) -> str:
        with self.connection:
            result = self.cursor.execute(
                "SELECT dish_price FROM menu WHERE id = ?",
                (id,)).fetchall()
        return result

    def get_g(self, id) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT dish_g FROM menu WHERE id = ?",
                (id,)).fetchall()
            return result

    # --- Взять рекомендации ---

    def restaurants_get_dish_rec_nutritionist(self, restaurant: str) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT dish_rec_nutritionist FROM menu WHERE rest_name = ?",
                (restaurant,)).fetchall()
            if len(result):
                if len(result[0]):
                    if result[0][0] is None:
                        return []
                    return result

    def restaurants_get_dish_rec_community(self, restaurant: str) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT dish_rec_community FROM menu WHERE rest_name = ?",
                (restaurant,)).fetchall()
            if len(result):
                if len(result[0]):
                    if result[0][0] is None:
                        return []
                    return result

    def restaurants_get_dish_rec_a_oblomov(self, restaurant: str) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT dish_rec_a_oblomov FROM menu WHERE rest_name = ?",
                (restaurant,)).fetchall()
            if len(result):
                if len(result[0]):
                    if result[0][0] is None:
                        return []
                    return result

    def restaurants_get_dish_rec_a_ivlev(self, restaurant: str) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT dish_rec_a_ivlev FROM menu WHERE rest_name = ?",
                (restaurant,)).fetchall()
            if len(result):
                if len(result[0]):
                    if result[0][0] is None:
                        return []
                    return result

    def restaurants_get_by_id(self, id) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM menu WHERE id = ?",
                (id,)).fetchall()
            return result[0]

    def restaurants_get_by_name(self, dish_name: str) -> list:
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM menu WHERE dish_name = ?",
                (dish_name,)).fetchall()
            return result[0]

    # --- review ---

    def restaurants_set_review(self, id: int, review: str):
        review = review.lower()

        symbols_to_remove = ":;/<>"

        for symbol in symbols_to_remove:
            review = review.replace(symbol, "")

        reviews = self.restaurants_get_review(id) + " ; " + review

        with self.connection:
            self.cursor.execute(
                "UPDATE menu SET stat_reviews = ? WHERE id = ?",
                (reviews, id))

    def restaurants_get_review(self, id: int) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT stat_reviews FROM menu WHERE id = ?",
                (id,)).fetchall()
            return str(result[0][0])

    # --- rating ---

    def restaurants_set_rating(self, id: int, rating: int):

        ratings = self.restaurants_get_rating(id) + " ; " + str(rating)

        with self.connection:
            self.cursor.execute(
                "UPDATE menu SET stat_rating = ? WHERE id = ?",
                (ratings, id))

    def restaurants_get_rating(self, id: int) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT stat_rating FROM menu WHERE id = ?",
                (id,)).fetchall()
            return str(result[0][0])

    def get_dish_simple_sostav(self, restaurant: str, name: str) -> str:
        with self.connection:
            result = self.connection.execute(
                "SELECT simple_ingridients FROM menu WHERE rest_name = ? and dish_name = ?",
                (restaurant, name)
            ).fetchall()
        return str(result[0][0])

    # --- for waiters ---

    def additional_dishes(self, dish_name):
        with self.connection:
            result = self.connection.execute(
                "SELECT additional_dishes FROM menu WHERE dish_name = ?", (dish_name,)
            ).fetchall()
        if result:
            return result[0][0]
        else:
            return None

    # ------

    def get_dish_size(self, id):
        with self.connection:
            result = self.connection.execute(
                "SELECT size FROM menu WHERE id = ?", (id,)
            ).fetchall()
        return str(result[0][0])

    # ======================================================================================================================
    # ===== ТАБЛИЦА: waiters =================================================================================================
    # ======================================================================================================================

    # --- Добавить значение ---

    def add_waiter(self, user_id, user_link, user_name=None, user_last_name=None, user_first_name=None,
                   user_surname=None, score="[]"):

        with self.connection:
            return self.cursor.execute(
                "INSERT INTO waiters (waiter_id, waiter_link, waiter_name, waiter_last_name,"
                " waiter_first_name, waiter_surname, waiter_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, user_link, user_name, user_last_name, user_first_name, user_surname, score))

    def del_waiter(self, user_id):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM waiters WHERE waiter_id = ?",
                (user_id,))

    def check_waiter_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM waiters WHERE waiter_id=?", (user_id,)).fetchall()
            return bool(len(result))

    def set_waiter_score(self, user_id: int, score: str):
        with self.connection:
            self.cursor.execute(
                "UPDATE waiters SET waiter_score = ? WHERE waiter_id = ?",
                (score, user_id))

    def get_waiter_score(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT waiter_score FROM waiters WHERE waiter_id=?",
                                         (user_id,)).fetchall()
            return result[0][0]

    def get_waiters_waiters(self):
        with self.connection:
            result = self.connection.execute("SELECT waiter_id FROM waiters").fetchall()
            users_id = []
            for row in result:
                users_id.append(int(row[0]))
            return users_id

    def get_waiters_names_and_stats(self):
        with self.connection:
            result = self.connection.execute(
                "SELECT waiter_id, waiter_last_name, waiter_first_name, waiter_surname, "
                "waiter_score, waiter_current_earnings, waiter_name FROM waiters").fetchall()
            return result

    def get_remark(self, waiter_id):
        with self.connection:
            result = self.connection.execute("SELECT waiter_remark FROM waiters WHERE waiter_id=?",
                                             (waiter_id,)).fetchall()
        return result[0][0]

    def set_remark(self, waiter_id, remark):
        with self.connection:
            self.cursor.execute(
                "UPDATE waiters SET waiter_remark = ? WHERE waiter_id = ?",
                (remark, waiter_id))

    def clear_remark(self, waiter_id):
        with self.connection:
            self.cursor.execute(
                "UPDATE waiters SET waiter_remark = ? WHERE waiter_id = ?",
                ('', waiter_id))

    def get_current_earnings(self, waiter_id):
        with self.connection:
            self.cursor.execute(
                "SELECT waiter_current_earnings FROM waiters WHERE waiter_id = ?",
                (waiter_id,))

    def set_current_earnings(self, amount, waiter_id):
        with self.connection:
            self.cursor.execute(
                "UPDATE waiters SET waiter_current_earnings = ? WHERE waiter_id = ?",
                (amount, waiter_id))

    def return_waiter_rest(self, waiter):
        with self.connection:
            result = self.cursor.execute(
                "SELECT waiter_rest FROM waiters WHERE waiter_id = ?",
                (waiter,)).fetchall()
        return result[0][0].split(':')[0]

    # ======================================================================================================================
    # ===== ТАБЛИЦА: baskets =================================================================================================
    # ======================================================================================================================

    def create_basket(self, user_id, basket="{}"):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO baskets (user_id, basket) VALUES (?, ?)",
                (user_id, json.dumps(basket)))

    def check_basket_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM baskets WHERE user_id=?", (user_id,)).fetchall()
            return bool(len(result))

    def set_basket(self, user_id, basket):
        with self.connection:
            self.cursor.execute(
                "UPDATE baskets SET basket = ? WHERE user_id = ?",
                (json.dumps(basket), user_id))

    def get_basket(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT basket FROM baskets WHERE user_id=?", (user_id,)).fetchall()
            try:
                return json.loads(result[0][0])
            except (json.JSONDecodeError, IndexError):
                return {}

    def set_qr_scanned(self, user_id, qr_scanned):
        with self.connection:
            self.cursor.execute(
                "UPDATE baskets SET qr_scanned = ? WHERE user_id = ?",
                (qr_scanned, user_id))

    def get_qr_scanned(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT qr_scanned FROM baskets WHERE user_id=?", (user_id,)).fetchall()
            return result[0][0]

    def set_qr_id(self, user_id, qr_id):
        with self.connection:
            self.cursor.execute(
                "UPDATE baskets SET qr_id = ? WHERE user_id = ?",
                (qr_id, user_id))

    def get_qr_id(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT qr_id FROM baskets WHERE user_id=?", (user_id,)).fetchall()
            return result[0][0]

    def del_basket(self, user_id):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM baskets WHERE user_id = ?",
                (user_id,))

    # ======================================================================================================================
    # ===== ТАБЛИЦА: user_actions =================================================================================================
    # ======================================================================================================================

    def get_last_session(self, user_id):
        self.cursor.execute('''
            SELECT session_num, actions, start_time, end_time
            FROM user_actions
            WHERE user_id = ?
            ORDER BY start_time DESC
            LIMIT 1
        ''', (user_id,))
        result = self.cursor.fetchone()
        return result

    def create_new_session(self, user_id, action):
        try:
            last_session = self.get_last_session(user_id)
        except:
            last_session = False
        SESSION_TIMEOUT = datetime.timedelta(hours=3)
        if last_session:
            last_session_num = last_session[0]
            last_start_time = datetime.datetime.strptime(last_session[2], '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() - last_start_time > SESSION_TIMEOUT:
                new_session_num = last_session_num + 1
            else:
                new_session_num = last_session_num
        else:
            new_session_num = 1
        current_time = datetime.datetime.now().replace(microsecond=0)

        self.cursor.execute('''
            INSERT INTO user_actions (user_id, session_num, actions, start_time)
            VALUES (?, ?, ?, ?)
        ''', (user_id, new_session_num, action, current_time.strftime('%Y-%m-%d %H:%M:%S')))

    def update_session(self, user_id, action):
        try:
            last_session = self.get_last_session(user_id)
        except:
            last_session = False
        if last_session:
            session_num, actions, start_time, end_time = last_session
            updated_actions = actions + '->' + action
            self.cursor.execute('''
                UPDATE user_actions
                SET actions = ?, end_time = ?
                WHERE user_id = ? AND session_num = ?
            ''', (updated_actions, datetime.datetime.now().replace(microsecond=0), user_id, session_num))

    def add_user_action(self, user_id, action):
        SESSION_TIMEOUT = datetime.timedelta(hours=3)
        try:
            last_session = self.get_last_session(user_id)
        except:
            last_session = False
        if last_session:
            last_start_time = datetime.datetime.strptime(last_session[2], '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() - last_start_time > SESSION_TIMEOUT:
                self.create_new_session(user_id, action)
            else:
                self.update_session(user_id, action)
        else:
            self.create_new_session(user_id, action)

    def check_last_action(self, user_id, action):
        try:
            last_session = self.get_last_session(user_id)
        except:
            return False
        if not last_session:
            return False
        last_action = last_session[1].split('->')
        if last_action[-1] == action:
            return True

    # ======================================================================================================================
    # ===== ТАБЛИЦА: stop_lists =================================================================================================
    # ======================================================================================================================

    def create_stop_list(self, rest, stop_list="{}"):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO stop_lists (rest, stop_list) VALUES (?, ?)",
                (rest, stop_list))

    def check_stop_list_exists(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM stop_lists").fetchall()
            return bool(len(result))

    def set_stop_list(self, stop_list):
        with self.connection:
            self.cursor.execute(
                "UPDATE stop_lists SET stop_list = ?",
                (stop_list,))

    def get_stop_list(self, rest):
        with self.connection:
            result = self.cursor.execute("SELECT stop_list FROM stop_lists WHERE rest=?", (rest,)).fetchall()
            return result[0][0]

    def del_stop_list(self, rest):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM stop_lists WHERE rest = ?",
                (rest,))

    # ======================================================================================================================
    # ===== ТАБЛИЦА: total_and_current_counts =================================================================================================
    # ======================================================================================================================

    def add_rest(self, rest, total_click_count=0, current_click_count=0, last_check_time=""):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO total_and_current_counts (rest, total_click_count, current_click_count,"
                " last_check_time) VALUES (?, ?, ?, ?)",
                (rest, total_click_count, current_click_count, last_check_time))

    def check_rest_exists(self, rest):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM total_and_current_counts WHERE rest=?", (rest,)).fetchall()
            return bool(len(result))

    def set_total_click_count(self, total_click_count):
        with self.connection:
            self.cursor.execute(
                "UPDATE total_and_current_counts SET total_click_count = ?",
                (total_click_count,))

    def get_total_click_count(self):
        with self.connection:
            result = self.cursor.execute("SELECT total_click_count FROM total_and_current_counts").fetchall()
        if len(result) > 0:
            return result[0][0]
        else:
            return None

    def set_current_click_count(self, current_click_count):
        with self.connection:
            self.cursor.execute(
                "UPDATE total_and_current_counts SET current_click_count = ?",
                (current_click_count,))

    def get_current_click_count(self):
        with self.connection:
            result = self.cursor.execute("SELECT current_click_count FROM total_and_current_counts").fetchall()
        if len(result) > 0:
            return result[0][0]
        else:
            return None

    def set_last_check_time(self, time):
        with self.connection:
            self.cursor.execute(
                "UPDATE total_and_current_counts SET last_check_time = ?",
                (time,))

    def get_last_check_time(self):
        with self.connection:
            result = self.cursor.execute("SELECT last_check_time FROM total_and_current_counts").fetchall()
            if len(result) > 0:
                return result[0][0]
            else:
                return None

    def del_rest(self, rest):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM total_and_current_counts WHERE rest = ?",
                (rest,))

    # ======================================================================================================================
    # ===== ТАБЛИЦА: admins =================================================================================================
    # ======================================================================================================================

    # --- Добавить значение ---

    def add_admin(self, user_id, user_rest):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO admins (admin_id, temp_rest) VALUES (?, ?)",
                (user_id, user_rest))

    def del_admin(self, user_id):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM admins WHERE admin_id = ?",
                (user_id,))

    def check_admin_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM admins WHERE admin_id=?", (user_id,)).fetchall()
            return bool(len(result))

    def set_admin_rest(self, user_id, rest):
        with self.connection:
            self.cursor.execute("UPDATE admins SET temp_rest = ? WHERE admin_id = ?", (rest, user_id,)).fetchall()

    def get_admin_rest(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT temp_rest FROM admins WHERE admin_id=?", (user_id,)).fetchall()
            return result[0][0]

    # ======================================================================================================================
    # ===== ТАБЛИЦА: orders =================================================================================================
    # ======================================================================================================================

    # --- Добавить значение ---

    def add_order(self, user_id, table_number, time, amount):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO orders (waiter_id, table_number, time, order_amount) VALUES (?, ?, ?, ?)",
                (user_id, table_number, time, amount))

    def get_current_guests_count(self):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        with self.connection:
            result = self.cursor.execute(f"SELECT time FROM orders WHERE time LIKE '%{current_time}%'").fetchall()
            if result:
                return len(result)
            else:
                return 0

    def get_current_waiter_guests(self, waiter_id):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        with self.connection:
            result = self.cursor.execute(
                f"SELECT time FROM orders WHERE waiter_id=? AND time LIKE '%{current_time}%'",
                (waiter_id,)).fetchall()
            if result:
                return len(result)
            else:
                return 0

    def get_current_waiter_sells(self, waiter_id):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        with self.connection:
            result = self.cursor.execute(
                f"SELECT order_amount FROM orders WHERE waiter_id=? AND time LIKE '%{current_time}%'",
                (waiter_id,)).fetchall()
            if result:
                return sum([int(e[0]) for e in result])
            else:
                return 0

    # ======================================================================================================================
    # ===== ТАБЛИЦА: orders_history =================================================================================================
    # ======================================================================================================================

    def add_users_order(self, user_id, rest, basket):
        with self.connection:
            return self.cursor.execute("INSERT INTO orders_history (user_id, rest, basket) VALUES (?, ?, ?)",
                                       (user_id, rest, basket))

    def get_last_users_order(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT rest FROM orders_history WHERE user_id={user_id}").fetchall()
            return result[-1]

    # ======================================================================================================================
    # ===== ТАБЛИЦА: client_rest_search =================================================================================================
    # ======================================================================================================================

    def add_search_filters(self, user_id, filters):
        with self.connection:
            return self.cursor.execute("INSERT INTO client_rest_search (id, filters, temp_rest) VALUES (?, ?, ?)",
                                       (user_id, filters, 0))

    def check_filters_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM client_rest_search WHERE id=?", (user_id,)).fetchall()
            return bool(len(result))

    def set_search_filters(self, user_id, filters):
        with self.connection:
            self.cursor.execute("UPDATE client_rest_search SET filters=? WHERE id=?",
                                (filters, user_id,)).fetchall()

    def get_search_filters(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT filters FROM client_rest_search WHERE id=?", (user_id,)).fetchall()
            return result[0][0]

    def set_temp_rest(self, user_id, temp_rest):
        with self.connection:
            self.cursor.execute("UPDATE client_rest_search SET temp_rest=? WHERE id=?",
                                (temp_rest, user_id,)).fetchall()

    def get_temp_rest(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT temp_rest FROM client_rest_search WHERE id=?",
                                         (user_id,)).fetchall()
            return result[0][0]

    # ======================================================================================================================
    # ===== ТАБЛИЦА: F2M_reviews =================================================================================================
    # ======================================================================================================================
    def add_reason(self, user_id, reason, star):
        with self.connection:
            return self.cursor.execute('INSERT INTO F2M_reviews (user_id, review, star) VALUES (?, ?, ?)',
                                       (user_id, reason, star))

    # ======================================================================================================================
    # ===== ТАБЛИЦА: iiko_data =================================================================================================
    # ======================================================================================================================

    def check_token(self, rest, api):
        try:
            with self.connection:
                result = self.cursor.execute("SELECT token_time_start FROM iiko_data WHERE rest_name = ?",
                                             (rest,)).fetchone()
                BASE_URL = "https://api-ru.iiko.services/api/1/"
                api_key = api

                if result:
                    date_format = "%Y-%m-%d %H:%M:%S.%f"
                    date_object = datetime.datetime.strptime(result[0], date_format)
                    one_hour = datetime.timedelta(hours=1)
                    time_diff = datetime.datetime.now() - date_object

                    if time_diff > one_hour:
                        self.cursor.execute("DELETE FROM iiko_data WHERE rest_name = ?", (rest,))
                        self.connection.commit()
                        return self.check_token(rest, api)

                    token = self.cursor.execute("SELECT iiko_rest_token FROM iiko_data WHERE rest_name = ?",
                                                (rest,)).fetchone()[0]
                    return token
                else:
                    url = f"{BASE_URL}access_token"
                    params = {"apiLogin": api_key}
                    response = requests.post(url, json=params)

                    if response.status_code != 200:
                        raise Exception(f"Failed to get token: {response.status_code}")

                    token = response.json().get("token")
                    if not token:
                        raise Exception("No token in response")

                    self.cursor.execute(
                        "INSERT INTO iiko_data (rest_name, iiko_rest_token, token_time_start) VALUES (?, ?, ?)",
                        (rest, token, datetime.datetime.now())
                    )
                    self.connection.commit()
                    return token

        except Exception as e:
            raise

    # ======================================================================================================================
    # ===== Действия с iiko_f =================================================================================================
    # ======================================================================================================================
    def get_iiko_id_by_name(self, name):
        with self.connection:
            result = self.connection.execute(
                'SELECT iiko_id FROM menu WHERE dish_name = ?',
                (name,)).fetchone()
        return result[0]

    def get_name_by_iiko_id(self, iiko_id, rest):
        with self.connection:
            result = self.connection.execute(
                'SELECT dish_name FROM menu WHERE iiko_id = ? and rest_name = ?',
                (iiko_id, rest)).fetchone()
            return result[0]

    # ======================================================================================================================
    # ===== f2m_waiter_bot =================================================================================================
    # ======================================================================================================================

    def get_chat_id_list(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM f2m_waiter_bot").fetchall()
            return result

    # ======================================================================================================================
    # ===== correlation_coefficients =================================================================================================
    # ======================================================================================================================

    def if_user_in_cc_table(self, user):
        with self.connection:
            result = self.cursor.execute("SELECT * from correlation_coefficient WHERE user_id = ?", (user,))
        if result[0] is None:
            self.create_cc_dict(user)
        else:
            return True

    def did_user_rate_the_dish(self, user, dish_id):
        with self.connection:
            result = self.cursor.execute(
                "SELECT users_dish_coefficients from correlation_coefficient WHERE user_id = ?", (user,))

    def save_dish_rating(self, user_id: int, dish_id: int, rating: int):
        with self.connection:
            # Получаем текущие коэффициенты пользователя
            result = self.cursor.execute(
                "SELECT users_dish_coefficients FROM correlation_coefficient WHERE user_id = ?",
                (user_id,)).fetchone()

            if result:
                # Если запись существует, обновляем её
                current_coefficients = eval(result[0]) if result[0] else {}

                # Если у блюда уже есть рейтинг, обновляем его
                if str(dish_id) in current_coefficients:
                    # Получаем текущий рейтинг и количество оценок
                    current_data = current_coefficients[str(dish_id)]
                    if isinstance(current_data, dict):
                        current_rating = current_data['rating']
                        current_count = current_data['count']
                        # Вычисляем новое среднее значение
                        new_rating = ((current_rating * current_count) + rating) / (current_count + 1)
                        current_coefficients[str(dish_id)] = {
                            'rating': new_rating,
                            'count': current_count + 1
                        }
                    else:
                        # Если старый формат (просто число), конвертируем в новый
                        current_coefficients[str(dish_id)] = {
                            'rating': (current_data + rating) / 2,
                            'count': 2
                        }
                else:
                    # Если это первая оценка блюда
                    current_coefficients[str(dish_id)] = {
                        'rating': rating,
                        'count': 1
                    }

                self.cursor.execute(
                    "UPDATE correlation_coefficient SET users_dish_coefficients = ? WHERE user_id = ?",
                    (str(current_coefficients), user_id)
                )
            else:
                # Если записи нет, создаём новую
                coefficients = {
                    str(dish_id): {
                        'rating': rating,
                        'count': 1
                    }
                }
                self.cursor.execute(
                    "INSERT INTO correlation_coefficient (user_id, users_dish_coefficients) VALUES (?, ?)",
                    (user_id, str(coefficients))
                )

    def create_cc_dict(self, user, cc="{}"):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO correlation_coefficient (rest, users_dish_coefficients) VALUES (?, ?)",
                (user, cc))

    # ======================================================================================================================
    # ===== users_anketa1 =================================================================================================
    # ======================================================================================================================
    def get_users_first_q(self, user_id):
        self.cursor.execute('''
                        SELECT * FROM users_anketa1 
                        WHERE user_id = ?
                    ''', (user_id,))
        row = self.cursor.fetchone()
        return row

    def set_default_q1(self, user_id):
        self.cursor.execute(''' INSERT INTO users_anketa1 
                                   VALUES (?, ?, ?, ?)
                               ''', (user_id, 'Спокойствие', '5/10', 'Мне как обычно'))
        self.connection.commit()

    def set_temp_users_mood(self, user, mood):
        self.cursor.execute('''UPDATE users_anketa1 SET mood = ? WHERE user_id = ?''', (mood, user))
        self.connection.commit()

    def get_temp_users_mood(self, user_id):
        self.cursor.execute('''
                        SELECT mood FROM users_anketa1
                        WHERE user_id = ?
                    ''', (user_id,))
        row = self.cursor.fetchone()
        return row[0]

    def set_temp_users_hungry(self, user, hungry):
        self.cursor.execute('''UPDATE users_anketa1 SET hungry = ? WHERE user_id = ?''', (hungry + '/10', user))
        self.connection.commit()

    def set_temp_users_prefers(self, user, prefer):
        self.cursor.execute('''UPDATE users_anketa1 SET prefers = ? WHERE user_id = ?''', (prefer, user))
        self.connection.commit()

    # ======================================================================================================================
    # ===== users_anketa2 =================================================================================================
    # ======================================================================================================================
    def set_default_q2(self, user_id):
        self.cursor.execute(''' INSERT INTO users_anketa2
                                   VALUES (?, ?, ?, ?, ?, ?, ?)
                               ''', (user_id, 'пусто', 'пусто', 'Стандартное', 'пусто', 'пусто', 'пусто'))
        self.connection.commit()

    def get_users_second_q(self, user_id):
        self.cursor.execute('''
                        SELECT * FROM users_anketa2
                        WHERE user_id = ?
                    ''', (user_id,))
        row = self.cursor.fetchone()
        return row

    def get_temp_users_ccal(self, user_id):
        self.cursor.execute('''
                        SELECT ccal FROM users_anketa2
                        WHERE user_id = ?
                    ''', (user_id,))
        row = self.cursor.fetchone()
        return row[0]

    def set_temp_users_sex(self, user, sex):
        self.cursor.execute('''UPDATE users_anketa2 SET sex = ? WHERE user_id = ?''', (sex, user))
        self.connection.commit()

    def set_temp_users_age(self, user, age):
        self.cursor.execute('''UPDATE users_anketa2 SET age = ? WHERE user_id = ?''', (age, user))
        self.connection.commit()

    def set_temp_users_food_style(self, user, food_style):
        self.cursor.execute('''UPDATE users_anketa2 SET food_style = ? WHERE user_id = ?''', (food_style, user))
        self.connection.commit()

    def get_temp_users_style(self, user_id):
        self.cursor.execute('''
                        SELECT food_style FROM users_anketa2
                        WHERE user_id = ?
                    ''', (user_id,))
        row = self.cursor.fetchone()
        return row[0]

    def set_temp_users_ccal(self, user, ccal):
        self.cursor.execute('''UPDATE users_anketa2 SET ccal = ? WHERE user_id = ?''', (ccal, user))
        self.connection.commit()

    def set_temp_users_dont_like_to_eat(self, user, dont_like_to_eat):
        self.cursor.execute('''UPDATE users_anketa2 SET dont_like_to_eat = ? WHERE user_id = ?''',
                            (dont_like_to_eat, user))
        self.connection.commit()

    def set_temp_users_like_to_eat(self, user, like_to_eat):
        self.cursor.execute('''UPDATE users_anketa2 SET like_to_eat = ? WHERE user_id = ?''', (like_to_eat, user))
        self.connection.commit()

    def get_temp_users_like_to_eat(self, user_id):
        self.cursor.execute('''
                        SELECT like_to_eat FROM users_anketa2
                        WHERE user_id = ?
                    ''', (user_id,))
        row = self.cursor.fetchone()
        return row[0]

    def get_temp_users_dont_like_to_eat(self, user_id):
        self.cursor.execute('''
                        SELECT dont_like_to_eat FROM users_anketa2
                        WHERE user_id = ?
                    ''', (user_id,))
        row = self.cursor.fetchone()
        return row[0]

    # ======================================================================================================================
    # ===== users_temp_all =================================================================================================
    # ======================================================================================================================

    def get_users_temp_message_id(self, user_id):
        self.cursor.execute('''SELECT temp_message_id FROM users_temp_all WHERE user_id = ?''', (user_id,))
        row = self.cursor.fetchone()
        return row

    def set_first_temp_mes_id(self, user, m_id):
        self.cursor.execute('''INSERT INTO users_temp_all VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
                            (user, m_id, None, None, None, None, None, None, None))
        self.connection.commit()

    def set_temp_users_message_id(self, user, m_id):
        self.cursor.execute('''UPDATE users_temp_all SET temp_message_id = ? WHERE user_id = ? ''', (m_id, user))
        self.connection.commit()

    def set_temp_users_state(self, user, state):
        self.cursor.execute('''UPDATE users_temp_all SET temp_users_state = ? WHERE user_id = ? ''', (state, user))
        self.connection.commit()

    def get_temp_users_state(self, user):
        self.cursor.execute('''SELECT temp_users_state FROM users_temp_all WHERE user_id = ?''', (user,))
        row = self.cursor.fetchone()
        return row[0]

    def set_first_message_to_delete(self, user, mes):
        self.cursor.execute('''UPDATE users_temp_all SET first_message_to_delete = ? WHERE user_id = ? ''', (mes, user))
        self.connection.commit()

    def get_first_message_to_delete(self, user):
        self.cursor.execute('''SELECT first_message_to_delete FROM users_temp_all WHERE user_id = ?''', (user,))
        row = self.cursor.fetchone()
        return row[0]

    def set_temp_users_category(self, user, category):
        self.cursor.execute('''UPDATE users_temp_all SET temp_users_category = ? WHERE user_id = ? ''',
                            (category, user))
        self.connection.commit()

    def get_temp_users_category(self, user):
        self.cursor.execute('''SELECT temp_users_category FROM users_temp_all WHERE user_id = ?''', (user,))
        row = self.cursor.fetchone()
        return row[0]

    def set_client_temp_dish(self, user_id: int, temp_dish: int):
        temp_dish = max(temp_dish, 0)
        with self.connection:
            self.cursor.execute(
                "UPDATE users_temp_all SET temp_users_dish = ? WHERE user_id = ?",
                (temp_dish, user_id))

    def get_client_temp_dish(self, user_id) -> int:
        with self.connection:
            result = self.connection.execute(
                "SELECT temp_users_dish FROM users_temp_all WHERE user_id = ?",
                (user_id,)).fetchall()
            return int(result[0][0])

    def set_temp_rec(self, user, rec):
        with self.connection:
            self.cursor.execute(
                "UPDATE users_temp_all SET temp_users_rec = ? WHERE user_id = ?",
                (rec, user))

    def get_temp_rec(self, user_id) -> int:
        with self.connection:
            result = self.connection.execute(
                "SELECT temp_users_rec FROM users_temp_all WHERE user_id = ?",
                (user_id,)).fetchall()
            return result[0][0]

    def set_temp_users_dish_id(self, user, rec):
        with self.connection:
            self.cursor.execute(
                "UPDATE users_temp_all SET temp_dish_id = ? WHERE user_id = ?",
                (rec, user))

    def get_temp_users_dish_id(self, user_id) -> int:
        with self.connection:
            result = self.connection.execute(
                "SELECT temp_dish_id FROM users_temp_all WHERE user_id = ?",
                (user_id,)).fetchall()
            return int(result[0][0])

    def set_temp_users_filial(self, user, filial):
        with self.connection:
            self.cursor.execute(
                "UPDATE users_temp_all SET filial = ? WHERE user_id = ?",
                (filial, user))

    def get_temp_users_filial(self, user_id) -> int:
        with self.connection:
            result = self.connection.execute(
                "SELECT filial FROM users_temp_all WHERE user_id = ?",
                (user_id,)).fetchall()
            return (result[0][0])

    # ======================================================================================================================
    # ===== ТАБЛИЦА: prefer_categories =================================================================================================
    # ======================================================================================================================

    def get_prefer_categories(self) -> list:
        """Получить список предпочтительных категорий"""
        with self.connection:
            result = self.connection.execute(
                "SELECT category_name, priority FROM prefer_categories ORDER BY priority ASC"
            ).fetchall()
            return [row[0] for row in result]

    def add_prefer_category(self, category_name: str, priority: int = 0):
        """Добавить категорию в предпочтительные"""
        with self.connection:
            self.cursor.execute(
                "INSERT INTO prefer_categories (category_name, priority) VALUES (?, ?)",
                (category_name, priority)
            )

    def remove_prefer_category(self, category_name: str):
        """Удалить категорию из предпочтительных"""
        with self.connection:
            self.cursor.execute(
                "DELETE FROM prefer_categories WHERE category_name = ?",
                (category_name,)
            )

    def update_prefer_category_priority(self, category_name: str, priority: int):
        """Обновить приоритет категории"""
        with self.connection:
            self.cursor.execute(
                "UPDATE prefer_categories SET priority = ? WHERE category_name = ?",
                (priority, category_name)
            )

    def clear_prefer_categories(self):
        """Очистить все предпочтительные категории"""
        with self.connection:
            self.cursor.execute("DELETE FROM prefer_categories")

    def get_prefer_categories_count(self) -> int:
        """Получить количество предпочтительных категорий"""
        with self.connection:
            result = self.connection.execute("SELECT COUNT(*) FROM prefer_categories").fetchone()
            return result[0]

    # ======================================================================================================================
    # ===== ТАБЛИЦА: logging =================================================================================================
    # ======================================================================================================================

    def add_logging_entry(self, user_id: str, date: str, fio: str = None, phone: str = None,
                          mood: str = None, hungry: str = None, style: str = None, sex: str = None,
                          age: str = None, dish_style: str = None, ccal: str = None,
                          dislike: str = None, like: str = None, order_time: str = None, sum_amount: int = None):
        """Добавить запись в таблицу logging"""
        with self.connection:
            self.cursor.execute("""
                        INSERT INTO logging (user_id, date, fio, phone, mood, hungry, style, sex, age,
                                           dish_style, ccal, dislike, like, "order", sum)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, date, fio, phone, mood, hungry, style, sex, age,
                          dish_style, ccal, dislike, like, order_time, sum_amount))

    def get_logging_by_user_id(self, user_id: str) -> list:
        """Получить все записи логов для пользователя"""
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM logging WHERE user_id = ? ORDER BY date DESC",
                (user_id,)
            ).fetchall()
            return result

    def get_logging_by_date(self, date: str) -> list:
        """Получить все записи логов за определённую дату"""
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM logging WHERE date LIKE ? ORDER BY date DESC",
                (f"%{date}%",)
            ).fetchall()
            return result

    def get_logging_all(self) -> list:
        """Получить все записи логов"""
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM logging ORDER BY date DESC"
            ).fetchall()
            return result

    def get_logging_by_id(self, log_id: int) -> tuple:
        """Получить запись лога по ID"""
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM logging WHERE id = ?",
                (log_id,)
            ).fetchone()
            return result

    def update_logging_fio(self, log_id: int, fio: str):
        """Обновить ФИО в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET fio = ? WHERE id = ?",
                (fio, log_id)
            )

    def update_logging_phone(self, log_id: int, phone: str):
        """Обновить телефон в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET phone = ? WHERE id = ?",
                (phone, log_id)
            )

    def update_logging_mood(self, log_id: int, mood: str):
        """Обновить настроение в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET mood = ? WHERE id = ?",
                (mood, log_id)
            )

    def update_logging_hungry(self, log_id: int, hungry: str):
        """Обновить уровень голода в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET hungry = ? WHERE id = ?",
                (hungry, log_id)
            )

    def update_logging_style(self, log_id: int, style: str):
        """Обновить стиль в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET style = ? WHERE id = ?",
                (style, log_id)
            )

    def update_logging_sex(self, log_id: int, sex: str):
        """Обновить пол в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET sex = ? WHERE id = ?",
                (sex, log_id)
            )

    def update_logging_age(self, log_id: int, age: str):
        """Обновить возраст в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET age = ? WHERE id = ?",
                (age, log_id)
            )

    def update_logging_dish_style(self, log_id: int, dish_style: str):
        """Обновить стиль блюд в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET dish_style = ? WHERE id = ?",
                (dish_style, log_id)
            )

    def update_logging_ccal(self, log_id: int, ccal: str):
        """Обновить калории в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET ccal = ? WHERE id = ?",
                (ccal, log_id)
            )

    def update_logging_dislike(self, log_id: int, dislike: str):
        """Обновить нелюбимые продукты в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET dislike = ? WHERE id = ?",
                (dislike, log_id)
            )

    def update_logging_like(self, log_id: int, like: str):
        """Обновить любимые продукты в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET like = ? WHERE id = ?",
                (like, log_id)
            )

    def update_logging_order(self, log_id: int, order_time: str):
        """Обновить время заказа в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET \"order\" = ? WHERE id = ?",
                (order_time, log_id)
            )

    def update_logging_sum(self, log_id: int, sum_amount: int):
        """Обновить сумму заказа в записи лога"""
        with self.connection:
            self.cursor.execute(
                "UPDATE logging SET sum = ? WHERE id = ?",
                (sum_amount, log_id)
            )

    def delete_logging_entry(self, log_id: int):
        """Удалить запись лога по ID"""
        with self.connection:
            self.cursor.execute(
                "DELETE FROM logging WHERE id = ?",
                (log_id,)
            )

    def get_logging_count(self) -> int:
        """Получить общее количество записей в логах"""
        with self.connection:
            result = self.connection.execute("SELECT COUNT(*) FROM logging").fetchone()
            return result[0]

    def get_logging_by_date_range(self, start_date: str, end_date: str) -> list:
        """Получить записи логов за период"""
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM logging WHERE date BETWEEN ? AND ? ORDER BY date DESC",
                (start_date, end_date)
            ).fetchall()
            return result

    # ======================================================================================================================
    # ===== УПРАВЛЕНИЕ СЕССИЯМИ ЛОГИРОВАНИЯ =================================================================================================
    # ======================================================================================================================

    def start_logging_session(self, user_id: str, date: str = None):
        """Начать новую сессию логирования"""
        if date is None:
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Создаём новую запись с базовыми данными
        self.add_logging_entry(
            user_id=user_id,
            date=date,
            fio=None,
            phone=None,
            mood=None,
            hungry=None,
            style=None,
            sex=None,
            age=None,
            dish_style=None,
            ccal=None,
            dislike=None,
            like=None,
            order_time=None,
            sum_amount=None
        )

    def get_current_logging_session(self, user_id: str) -> tuple:
        """Получить текущую активную сессию пользователя (последнюю запись)"""
        with self.connection:
            result = self.connection.execute(
                "SELECT * FROM logging WHERE user_id = ? ORDER BY date DESC LIMIT 1",
                (user_id,)
            ).fetchone()
            return result

    def update_logging_session_mood(self, user_id: str, mood: str):
        """Обновить настроение в текущей сессии"""
        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_mood(current_session[0], mood)

    def update_logging_session_hungry(self, user_id: str, hungry: str):
        """Обновить уровень голода в текущей сессии"""
        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_hungry(current_session[0], hungry)

    def update_logging_session_style(self, user_id: str, style: str):
        """Обновить стиль в текущей сессии"""
        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_style(current_session[0], style)

    def update_logging_session_sex(self, user_id: str, sex: str):
        """Обновить пол в текущей сессии"""
        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_sex(current_session[0], sex)

    def update_logging_session_age(self, user_id: str, age: str):
        """Обновить возраст в текущей сессии"""
        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_age(current_session[0], age)

    def update_logging_session_dish_style(self, user_id: str, dish_style: str):
        """Обновить стиль блюд в текущей сессии"""
        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_dish_style(current_session[0], dish_style)

    def update_logging_session_ccal(self, user_id: str, ccal: str):
        """Обновить калории в текущей сессии"""
        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_ccal(current_session[0], ccal)

    def update_logging_session_dislike(self, user_id: str, dislike: str):
        """Обновить нелюбимые продукты в текущей сессии"""
        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_dislike(current_session[0], dislike)

    def update_logging_session_like(self, user_id: str, like: str):
        """Обновить любимые продукты в текущей сессии"""
        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_like(current_session[0], like)

    def update_logging_session_order(self, user_id: str, order_composition: str = None):
        """Обновить состав заказа в текущей сессии"""
        if order_composition is None:
            order_composition = "Заказ не оформлен"

        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_order(current_session[0], order_composition)

    def update_logging_session_sum(self, user_id: str, sum_amount: int):
        """Обновить сумму заказа в текущей сессии"""
        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_sum(current_session[0], sum_amount)

    def update_logging_session_phone(self, user_id: str, phone: str):
        """Обновить телефон в текущей сессии"""
        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_phone(current_session[0], phone)

    def update_logging_session_fio(self, user_id: str, fio: str):
        """Обновить ФИО в текущей сессии"""
        current_session = self.get_current_logging_session(user_id)
        if current_session:
            self.update_logging_fio(current_session[0], fio)

    def get_dish_price_by_name(self, name):
        with self.connection:
            result = self.cursor.execute(
                "SELECT dish_price FROM menu WHERE dish_name = ?",
                (name,)).fetchone()
        return int(result[0])