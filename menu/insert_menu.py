from naim.config import db
import pandas as pd
conn = db.return_connect()
cursor = conn.cursor()
df_excel = pd.read_excel('меню_с_весом.xlsx', sheet_name=0, engine='openpyxl')
id = 1
for index, row in df_excel.iterrows():
    dish_category = row[0]
    dish_name = row[1]
    dish_neuro_cam = row[7]
    dish_ing = row[2]
    simple = row[2]
    kbzhu = row[8]
    dish_g = row[10]
    dish_price = row[3]
    size = None
    iiko_id = row[4]
    dish_style = row[5]
    dish_mood = 'Радость, Печаль, Гнев, Спокойствие, Волнение'
    dish_rec_n = row[6]
    url = 'https://koreanchick.ru/'
    additional = ''
    stat = ''
    stat_r = ''
    foodToMoodCoin = ''
    cursor.execute(
        "INSERT INTO menu (id, dish_category, dish_name, dish_neuro_cam, dish_ingredients, simple_ingridients, dish_kbzhu, dish_g, dish_price, size, iiko_id, dish_style, dish_mood, dish_rec_nutritionist, url, additional_dishes, stat_rating, stat_reviews, foodToMoodCoin) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (id, dish_category, dish_name, dish_neuro_cam, dish_ing, simple, kbzhu, f'{dish_g[:-1]}', dish_price, size, iiko_id, dish_style, dish_mood, dish_rec_n, url, additional, stat, stat_r, foodToMoodCoin))
    id += 1

conn.commit()
conn.close()

print("✅ Данные успешно перенесены из CSV в SQLite!")
