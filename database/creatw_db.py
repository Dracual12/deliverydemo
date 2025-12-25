import sqlite3
import os


def create_database_structure(db_file):
    """Создает полную структуру базы данных F2M"""

    # Удаляем существующий файл, если он есть
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"🗑️ Удален существующий файл: {db_file}")

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    print(f"🔨 Создаю новую базу данных: {db_file}")
    print("=" * 80)

    # 1. Таблица users
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER NOT NULL DEFAULT 0,
            user_link TEXT NOT NULL DEFAULT "tg://user?id=",
            user_name TEXT,
            user_first_name TEXT,
            user_last_name TEXT,
            user_reg_time TEXT NOT NULL,
            first_message INTEGER NOT NULL DEFAULT 0,
            last_message INTEGER NOT NULL DEFAULT 0,
            mode_id INTEGER NOT NULL DEFAULT 0,
            mode_key TEXT NOT NULL DEFAULT '',
            ban INTEGER NOT NULL DEFAULT 0,
            user_verification NUMERIC,
            foodToMoodCoin INTEGER,
            last_recomendation_time TEXT
        )
    ''')
    print("✅ Создана таблица: users")

    # 2. Таблица clients
    cursor.execute('''
        CREATE TABLE clients (
            id INTEGER NOT NULL,
            username TEXT,
            sex TEXT,
            age TEXT,
            style TEXT,
            blacklist TEXT,
            temp_rest TEXT,
            temp_state TEXT,
            temp_recommendation TEXT,
            temp_category TEXT,
            temp_dish INTEGER NOT NULL DEFAULT 0,
            temp_dish_id INTEGER NOT NULL DEFAULT 0,
            can_alert INTEGER NOT NULL DEFAULT 0,
            last_qr_time INTEGER NOT NULL DEFAULT 0,
            rec_message_id INTEGER,
            recommendation TEXT,
            whitelist TEXT,
            ccal INTEGER
        )
    ''')
    print("✅ Создана таблица: clients")

    # 3. Таблица restaurants
    cursor.execute('''
        CREATE TABLE restaurants (
            id INTEGER,
            rest_name TEXT,
            rest_address TEXT,
            dish_category TEXT,
            dish_name TEXT,
            dish_disc TEXT,
            dish_ingredients TEXT,
            dish_style TEXT,
            dish_mood TEXT,
            dish_rec_nutritionist TEXT,
            dish_rec_community TEXT,
            dish_rec_a_oblomov TEXT,
            dish_rec_a_ivlev TEXT,
            stat_reviews TEXT,
            stat_rating TEXT,
            foodToMoodCoin TEXT,
            url TEXT,
            dish_price INTEGER,
            dish_g TEXT,
            simple_ingridients TEXT,
            additional_dishes TEXT,
            size TEXT,
            iiko_id TEXT
        )
    ''')
    print("✅ Создана таблица: restaurants")

    # 4. Таблица waiters
    cursor.execute('''
        CREATE TABLE waiters (
            waiter_id INTEGER,
            waiter_rest TEXT,
            waiter_link TEXT,
            waiter_name TEXT,
            waiter_last_name TEXT NOT NULL,
            waiter_first_name TEXT NOT NULL,
            waiter_surname TEXT NOT NULL,
            waiter_score TEXT NOT NULL DEFAULT '[]',
            waiter_remark TEXT DEFAULT "",
            waiter_current_earnings INTEGER NOT NULL DEFAULT 0
        )
    ''')
    print("✅ Создана таблица: waiters")

    # 5. Таблица waiter (отдельная таблица)
    cursor.execute('''
        CREATE TABLE waiter (
            waiter_id INTEGER PRIMARY KEY,
            waiter_name TEXT,
            waiter_first_name TEXT,
            waiter_last_name TEXT,
            waiter_surname TEXT,
            waiter_rest TEXT,
            waiter_score REAL,
            waiter_current_earnings REAL
        )
    ''')
    print("✅ Создана таблица: waiter")

    # 6. Таблица baskets
    cursor.execute('''
        CREATE TABLE baskets (
            user_id INTEGER DEFAULT 0,
            basket TEXT DEFAULT '{}',
            qr_scanned INTEGER DEFAULT 0,
            qr_id INTEGER DEFAULT 0
        )
    ''')
    print("✅ Создана таблица: baskets")

    # 7. Таблица user_actions
    cursor.execute('''
        CREATE TABLE user_actions (
            id INTEGER,
            user_id INTEGER,
            session_num INTEGER,
            actions TEXT,
            start_time TEXT,
            end_time TEXT
        )
    ''')
    print("✅ Создана таблица: user_actions")

    # 8. Таблица bosses
    cursor.execute('''
        CREATE TABLE bosses (
            boss_id INTEGER NOT NULL,
            boss_rest TEXT NOT NULL
        )
    ''')
    print("✅ Создана таблица: bosses")

    # 9. Таблица stop_lists
    cursor.execute('''
        CREATE TABLE stop_lists (
            rest TEXT NOT NULL,
            stop_list TEXT
        )
    ''')
    print("✅ Создана таблица: stop_lists")

    # 10. Таблица total_and_current_counts
    cursor.execute('''
        CREATE TABLE total_and_current_counts (
            rest TEXT,
            total_click_count INTEGER,
            current_click_count INTEGER,
            last_check_time TEXT
        )
    ''')
    print("✅ Создана таблица: total_and_current_counts")

    # 11. Таблица admins
    cursor.execute('''
        CREATE TABLE admins (
            admin_id INTEGER,
            temp_rest TEXT
        )
    ''')
    print("✅ Создана таблица: admins")

    # 12. Таблица orders
    cursor.execute('''
        CREATE TABLE orders (
            waiter_id INTEGER,
            rest TEXT,
            table_number TEXT,
            time TEXT,
            order_amount INTEGER
        )
    ''')
    print("✅ Создана таблица: orders")

    # 13. Таблица orders_history
    cursor.execute('''
        CREATE TABLE orders_history (
            orders_id INTEGER NOT NULL PRIMARY KEY,
            user_id INTEGER,
            rest TEXT,
            basket TEXT
        )
    ''')
    print("✅ Создана таблица: orders_history")

    # 14. Таблица client_rest_search
    cursor.execute('''
        CREATE TABLE client_rest_search (
            id INTEGER,
            filters TEXT,
            temp_rest INTEGER
        )
    ''')
    print("✅ Создана таблица: client_rest_search")

    # 15. Таблица rest_filters_parameters
    cursor.execute('''
        CREATE TABLE rest_filters_parameters (
            rest_name TEXT NOT NULL,
            rest_address TEXT NOT NULL,
            kitchen TEXT NOT NULL,
            bill TEXT NOT NULL
        )
    ''')
    print("✅ Создана таблица: rest_filters_parameters")

    # 16. Таблица F2M_reviews
    cursor.execute('''
        CREATE TABLE F2M_reviews (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            review TEXT,
            star INTEGER
        )
    ''')
    print("✅ Создана таблица: F2M_reviews")

    # 17. Таблица iiko_data
    cursor.execute('''
        CREATE TABLE iiko_data (
            rest_name TEXT,
            iiko_rest_token TEXT,
            token_time_start TEXT
        )
    ''')
    print("✅ Создана таблица: iiko_data")

    # 18. Таблица f2m_waiter_bot
    cursor.execute('''
        CREATE TABLE f2m_waiter_bot (
            chat_id INTEGER NOT NULL,
            rest TEXT,
            plan INTEGER
        )
    ''')
    print("✅ Создана таблица: f2m_waiter_bot")

    # 19. Таблица correlation_coefficient
    cursor.execute('''
        CREATE TABLE correlation_coefficient (
            user_id TEXT,
            users_dish_coefficients TEXT
        )
    ''')
    print("✅ Создана таблица: correlation_coefficient")

    # 20. Таблица prime_hill_users
    cursor.execute('''
        CREATE TABLE prime_hill_users (
            user_id INTEGER PRIMARY KEY,
            phone TEXT,
            prime_hill_id TEXT,
            points TEXT DEFAULT '{}'
        )
    ''')
    print("✅ Создана таблица: prime_hill_users")

    # 21. Таблица premium_bonus
    cursor.execute('''
        CREATE TABLE premium_bonus (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            is_registered BOOLEAN DEFAULT "FALSE",
            blocked BOOLEAN DEFAULT "FALSE",
            phone TEXT,
            card_number TEXT,
            surname TEXT,
            name TEXT,
            middle_name TEXT,
            birth_date TEXT,
            gender TEXT,
            email TEXT,
            child1_birth_date TEXT,
            child1_name TEXT,
            child1_gender TEXT,
            child2_birth_date TEXT,
            child2_name TEXT,
            child2_gender TEXT,
            child3_birth_date TEXT,
            child3_name TEXT,
            child3_gender TEXT,
            child4_birth_date TEXT,
            child4_name TEXT,
            child4_gender TEXT,
            group_id TEXT,
            group_name TEXT,
            balance INTEGER DEFAULT 0,
            balance_bonus_accumulated INTEGER DEFAULT 0,
            balance_bonus_present INTEGER DEFAULT 0,
            balance_bonus_action INTEGER DEFAULT 0,
            bonus_inactive INTEGER DEFAULT 0,
            bonus_next_activation_text TEXT,
            phone_checked BOOLEAN DEFAULT "FALSE",
            is_refused_receive_messages BOOLEAN DEFAULT "FALSE",
            is_refused_receive_emails BOOLEAN DEFAULT "FALSE",
            is_agreed_receive_electronic_receipt BOOLEAN DEFAULT "FALSE",
            additional_info TEXT,
            init_purchase_count INTEGER DEFAULT 0,
            init_payment_amount INTEGER DEFAULT 0,
            external_id TEXT,
            city_id TEXT,
            city_name TEXT,
            client_id INTEGER,
            bonus_reserved INTEGER DEFAULT 0,
            write_off_confirmation_required BOOLEAN DEFAULT "FALSE",
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Создана таблица: premium_bonus")

    # 22. Таблица loyalty_programs
    cursor.execute('''
        CREATE TABLE loyalty_programs (
            id INTEGER PRIMARY KEY,
            restaurant_name TEXT NOT NULL,
            program_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Создана таблица: loyalty_programs")

    # 23. Таблица reviews
    cursor.execute('''
        CREATE TABLE reviews (
            date TEXT,
            user_name TEXT,
            rating INTEGER,
            review TEXT,
            dish_name TEXT,
            restaurant_name TEXT
        )
    ''')
    print("✅ Создана таблица: reviews")

    # 24. Таблица tickets
    cursor.execute('''
        CREATE TABLE tickets (
            ticket_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            chat_id INTEGER,
            username TEXT,
            subject TEXT,
            description TEXT,
            date TEXT
        )
    ''')
    print("✅ Создана таблица: tickets")

    # 25. Таблица chats
    cursor.execute('''
        CREATE TABLE chats (
            chat_id INTEGER PRIMARY KEY,
            rest TEXT,
            plan INTEGER
        )
    ''')
    print("✅ Создана таблица: chats")

    # 26. Таблица prefer_categories
    cursor.execute('''
        CREATE TABLE prefer_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Создана таблица: prefer_categories")

    # Создаем индексы
    cursor.execute('CREATE INDEX idx_orders_waiter_id ON orders(waiter_id)')
    print("✅ Создан индекс: idx_orders_waiter_id")

    # Создаем виртуальные таблицы для полнотекстового поиска
    cursor.execute('CREATE VIRTUAL TABLE rest_fts USING fts4(id, rest_name, rest_address)')
    print("✅ Создана виртуальная таблица: rest_fts")

    cursor.execute('CREATE VIRTUAL TABLE dish_fts USING fts4(id, rest_name, rest_address, dish_name)')
    print("✅ Создана виртуальная таблица: dish_fts")

    conn.commit()
    conn.close()

    print("=" * 80)
    print("🎉 База данных успешно создана!")
    print(f"�� Файл: {db_file}")
    print(f"�� Создано таблиц: 25 основных + 2 виртуальные")
    print("�� Создан индекс: idx_orders_waiter_id")
    print()
    print("💡 Теперь ты можешь использовать эту базу данных в своей программе!")


if __name__ == "__main__":
    create_database_structure('/files/databse.db')