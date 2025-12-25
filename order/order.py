from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    ReplyKeyboardMarkup, InlineQuery, InputTextMessageContent, InlineQueryResultArticle
from config import db, dp, bot
from iiko_f import iiko
from aiogram import types


@dp.inline_handler()
async def choose_rest(inline_query: InlineQuery):
    user = inline_query.from_user.id
    query = inline_query.query.lower()  # текст, который ввёл пользователь
    offset = int(inline_query.offset) if inline_query.offset else 0
    limit = 20

    # Получаем все блюда
    dishes = db.restaurants_get_all_dish()

    # Фильтруем блюда по запросу пользователя
    if query:
        dishes = [e for e in dishes if query in e[1].lower()]

    results = []
    for e in dishes[offset:offset+limit]:
            dish_id = e[0]
            dish_name = e[1]
            result = InlineQueryResultArticle(
            id=str(dish_id) + '_' + str(offset),
                title=f"«{dish_name}»",
                description='',
                input_message_content=InputTextMessageContent(f'«{dish_name}»'),
            )
            results.append(result)

    next_offset = str(offset + limit) if offset + limit < len(dishes) else ''
    await inline_query.answer(results, cache_time=1, next_offset=next_offset)
