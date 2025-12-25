import datetime
from uuid import uuid4
import asyncio
import time
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv
from aiogram.utils.deep_linking import decode_payload
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, \
    ReplyKeyboardMarkup, InlineQuery, InputTextMessageContent, InlineQueryResultArticle
from config import dp, bot, db
from handlers.message_handlers import *
from order_and_web_app import *
import menu.categories
import menu.card
import order.order
import handlers.admin_categories
import os

# Импортируем start_bot ПОСЛЕ всех остальных модулей, чтобы избежать циклических импортов
# Обработчики стартового меню уже определены в start_bot.py и будут зарегистрированы последними
from start_bot import *

load_dotenv()


async def start_handler(message: types.Message):
    try:
        user = message.from_user.id
        user_id = str(user)
        reg_time = datetime.utcnow().replace(microsecond=0)

        # Оптимизируем операции с БД - делаем их быстрее
        # Проверяем существование пользователя один раз
        user_exists = db.check_users_user_exists(user)
        
        # Логируем ФИО пользователя в сессию (не блокируем выполнение)
        try:
            fio = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
            if fio:
                db.update_logging_session_fio(user_id, fio)
        except Exception as e:
            print(f"Error updating session FIO: {e}")

        # Работа с корзиной
        try:
            if db.check_basket_exists(user):
                db.set_basket(user, "{}")
            else:
                db.create_basket(user)
        except Exception as e:
            print(f"Error with basket: {e}")

        # Регистрация нового пользователя
        if not user_exists:
            try:
                db.add_users_user(
                    user,
                    f'tg://user?id={user}',
                    reg_time,
                    message.from_user.username,
                    message.from_user.first_name,
                    message.from_user.last_name
                )
                db.set_default_q1(user)
                db.set_default_q2(user)
                db.set_users_mode(user, 0, 'start')
            except Exception as e:
                print(f"Error adding new user: {e}")

        # Получаем ID предыдущих сообщений
        try:
            first = int(db.get_users_first_message(user) or 0)
            last = int(db.get_users_last_message(user) or 0)
        except:
            first = 0
            last = 0

        # Очистка чата: ограничиваем количество удалений и делаем это асинхронно
        # Удаляем максимум 5 последних сообщений, чтобы не блокировать выполнение
        if first != 0 and last != 0 and last > first:
            messages_to_delete = min(5, last - first + 1)  # Ограничиваем до 5 сообщений
            delete_tasks = []
            for i in range(max(first, last - messages_to_delete + 1), last + 1):
                delete_tasks.append(bot.delete_message(user, i))
            
            # Удаляем сообщения параллельно с таймаутом
            if delete_tasks:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*delete_tasks, return_exceptions=True),
                        timeout=1.5  # Максимум 1.5 секунды на удаление
                    )
                except asyncio.TimeoutError:
                    pass  # Игнорируем таймаут, продолжаем работу

        # Сбрасываем счетчики сообщений
        db.set_users_first_message(user, 0)
        db.set_users_last_message(user, 0)

        # Устанавливаем режим пользователя
        try:
            db.set_users_mode(user, 0, 'start')
        except Exception as e:
            print(f"Error setting user mode: {e}")

        # Отправляем приветственное сообщение
        text = ("👋 Добро пожаловать в <b>KoreanChick</b>!\n"
                "Я — виртуальный ассистент нашей сети ресторанов.\n"
                "Здесь можно:\n\n"
                "• 🛒 сделать заказ\n"
                "• ❓ узнать ответы на частые вопросы\n"
                "• 📍 посмотреть адреса и контакты ресторанов\n\n"
                "С чем могу помочь?")

        try:
            message_obj = await asyncio.wait_for(
                bot.send_message(
                    chat_id=user,
                    text=text,
                    parse_mode='HTML',
                    reply_markup=buttons_start_02()
                ),
                timeout=5.0  # Таймаут 5 секунд для отправки сообщения
            )
            
            # Сохраняем ID нового сообщения (не блокируем выполнение)
            try:
                if db.get_users_temp_message_id(user) is None:
                    db.set_first_temp_mes_id(user, message_obj.message_id)
                else:
                    db.set_temp_users_message_id(user, message_obj.message_id)
                db.set_users_first_message(user, message_obj.message_id)
                db.set_users_last_message(user, message_obj.message_id)
            except Exception as e:
                print(f"Error saving message ID: {e}")
        except asyncio.TimeoutError:
            print(f"Timeout sending message to user {user}")
            # Пытаемся отправить без форматирования
            try:
                await bot.send_message(chat_id=user, text="👋 Добро пожаловать в KoreanChick!")
            except:
                pass
    except Exception as e:
        print(f"Error in start_handler: {e}")
        import traceback
        traceback.print_exc()
        try:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Произошла ошибка при запуске. Попробуйте позже.")
        except:
            pass


@dp.message_handler(commands=['start', 'restart'])
async def start_command(message: types.Message):
    print('start2')
    try:
        user = message.from_user.id
        print(f"Start command received from user {user} at {time.time()}")
        
        # СРАЗУ отправляем ответ пользователю, чтобы он видел реакцию бота
        text = ("👋 Добро пожаловать в <b>KoreanChick</b>!\n"
                "Я — виртуальный ассистент нашей сети ресторанов.\n"
                "Здесь можно:\n\n"
                "• 🛒 сделать заказ\n"
                "• ❓ узнать ответы на частые вопросы\n"
                "• 📍 посмотреть адреса и контакты ресторанов\n\n"
                "С чем могу помочь?")
        
        # Отправляем сообщение СРАЗУ
        try:
            message_obj = await asyncio.wait_for(
                bot.send_message(
                    chat_id=user,
                    text=text,
                    parse_mode='HTML',
                    reply_markup=buttons_start_02()
                ),
                timeout=3.0
            )
            print(f"Message sent to user {user} at {time.time()}")
        except asyncio.TimeoutError:
            print(f"Timeout sending message to user {user}")
            return
        except Exception as e:
            print(f"Error sending message: {e}")
            return
        
        # Проверяем наличие аргументов
        args = message.get_args()
        if args:
            # Обработка аргументов (для официантов и т.д.)
            try:
                decoded_args = decode_payload(args)
                if "or" in decoded_args[:2]:
                    if db.check_waiter_exists(user):
                        db.clear_remark(user)
                        from waiters import waiter_start as w_start
                        await w_start.get_order(message, decoded_args[2:])
                        return
                    else:
                        await bot.send_message(chat_id=user, text="Вы не зарегистрированы как официант")
                        return
            except Exception as e:
                print(f"Error decoding args: {e}")
        
        # Выполняем остальные операции в фоне (не блокируем ответ)
        asyncio.create_task(process_start_background(
            user, 
            user_id=str(user), 
            message_obj=message_obj,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username
        ))
        
    except Exception as e:
        print(f"Error in start_command: {e}")
        import traceback
        traceback.print_exc()
        try:
            await bot.send_message(chat_id=message.from_user.id,
                                  text="Произошла ошибка. Попробуйте позже.")
        except:
            pass


async def process_start_background(user, user_id, message_obj, first_name=None, last_name=None, username=None):
    """Выполняет фоновые операции после отправки ответа пользователю"""
    try:
        reg_time = datetime.utcnow().replace(microsecond=0)
        
        # Начинаем новую сессию логирования (в фоне)
        try:
            db.start_logging_session(user_id)
        except Exception as e:
            print(f"Error in start_logging_session: {e}")
        
        # Оптимизируем операции с БД
        user_exists = db.check_users_user_exists(user)
        
        # Логируем ФИО пользователя в сессию (в фоне)
        try:
            fio = f"{first_name or ''} {last_name or ''}".strip()
            if fio:
                db.update_logging_session_fio(user_id, fio)
        except Exception as e:
            print(f"Error updating session FIO: {e}")

        # Работа с корзиной
        try:
            if db.check_basket_exists(user):
                db.set_basket(user, "{}")
            else:
                db.create_basket(user)
        except Exception as e:
            print(f"Error with basket: {e}")

        # Регистрация нового пользователя
        if not user_exists:
            try:
                db.add_users_user(
                    user,
                    f'tg://user?id={user}',
                    reg_time,
                    username,
                    first_name,
                    last_name
                )
                db.set_default_q1(user)
                db.set_default_q2(user)
                db.set_users_mode(user, 0, 'start')
            except Exception as e:
                print(f"Error adding new user: {e}")

        # Получаем ID предыдущих сообщений
        try:
            first = int(db.get_users_first_message(user) or 0)
            last = int(db.get_users_last_message(user) or 0)
        except:
            first = 0
            last = 0

        # Очистка чата: ограничиваем количество удалений
        if first != 0 and last != 0 and last > first:
            messages_to_delete = min(3, last - first + 1)  # Ограничиваем до 3 сообщений
            delete_tasks = []
            for i in range(max(first, last - messages_to_delete + 1), last + 1):
                delete_tasks.append(bot.delete_message(user, i))
            
            if delete_tasks:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*delete_tasks, return_exceptions=True),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    pass

        # Сохраняем ID нового сообщения
        try:
            if db.get_users_temp_message_id(user) is None:
                db.set_first_temp_mes_id(user, message_obj.message_id)
            else:
                db.set_temp_users_message_id(user, message_obj.message_id)
            db.set_users_first_message(user, message_obj.message_id)
            db.set_users_last_message(user, message_obj.message_id)
            db.set_users_first_message(user, 0)  # Сбрасываем счетчики
            db.set_users_last_message(user, 0)
            db.set_qr_scanned(user, False)
            db.set_users_mode(user, 0, 'start')
        except Exception as e:
            print(f"Error saving message ID: {e}")
            
    except Exception as e:
        print(f"Error in process_start_background: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"Error in start_command: {e}")
        import traceback
        traceback.print_exc()
        try:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Произошла ошибка. Попробуйте позже.")
        except:
            pass


def buttons_start_02():
    menu = InlineKeyboardMarkup(row_width=1)

    btn1 = InlineKeyboardButton(text="🛒 Сделать заказ",
                                callback_data="make_order")

    btn2 = InlineKeyboardButton(text="❓FAQ",
                                callback_data="faq")
    btn3 = InlineKeyboardButton(text="📍Контакты ",
                                callback_data="contacts")

    menu.add(btn1)
    menu.add(btn2)
    menu.add(btn3)

    return menu

if __name__ == '__main__':
    # Запускаем бота
    print('start')
    executor.start_polling(dp)
