from config import dp, db
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@dp.message_handler(commands=['admin_categories'])
async def admin_categories_menu(message: types.Message):
    """Главное меню управления категориями"""
    if not db.check_admin_exists(message.from_user.id):
        await message.answer("У вас нет доступа к админ-панели.")
        return
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📋 Показать категории", callback_data="show_categories2"),
        InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category"),
        InlineKeyboardButton("❌ Удалить категорию", callback_data="remove_category"),
        InlineKeyboardButton("🔄 Изменить приоритет", callback_data="change_priority"),
        InlineKeyboardButton("🗑 Очистить все", callback_data="clear_categories")
    )
    
    await message.answer("🎛 Панель управления предпочтительными категориями", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data == "show_categories2")
async def show_categories(call: types.CallbackQuery):
    await call.answer()
    """Показать текущие предпочтительные категории"""
    categories = db.get_prefer_categories()
    
    if not categories:
        await call.message.edit_text("📋 Предпочтительные категории не настроены.\n\nИспользуйте кнопки ниже для управления.")
        await show_categories_menu(call.message)
    else:
        text = "📋 Текущие предпочтительные категории:\n\n"
        for i, category in enumerate(categories, 1):
            text += f"{i}. {category}\n"
        
        await call.message.edit_text(text)
        await show_categories_menu(call.message)


async def show_categories_for_message(message: types.Message):
    """Показать категории для объекта Message (используется в других функциях)"""
    categories = db.get_prefer_categories()
    
    if not categories:
        await message.answer("📋 Предпочтительные категории не настроены.\n\nИспользуйте кнопки ниже для управления.")
        await show_categories_menu(message)
    else:
        text = "📋 Текущие предпочтительные категории:\n\n"
        for i, category in enumerate(categories, 1):
            text += f"{i}. {category}\n"
        
        await message.answer(text)
        await show_categories_menu(message)

async def show_categories_menu(message):
    """Показать меню управления категориями"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category"),
        InlineKeyboardButton("❌ Удалить категорию", callback_data="remove_category"),
        InlineKeyboardButton("🔄 Изменить приоритет", callback_data="change_priority"),
        InlineKeyboardButton("🗑 Очистить все", callback_data="clear_categories"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_admin_c")
    )
    
    await message.answer("🎛 Управление категориями", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data == "add_category")
async def add_category_start(call: types.CallbackQuery):
    """Начать добавление категории"""

    await call.answer()
    # Получаем все доступные категории из меню
    all_categories = db.get_all_categories()
    prefer_categories = db.get_prefer_categories()
    
    # Фильтруем только те, которые ещё не добавлены
    available_categories = [cat for cat in all_categories if cat not in prefer_categories]
    
    if not available_categories:
        await call.message.edit_text("❌ Все доступные категории уже добавлены в предпочтительные.")
        await show_categories_menu(call.message)
        return
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    for category in available_categories[:10]:  # Показываем первые 10
        keyboard.add(InlineKeyboardButton(category, callback_data=f"select_cat_{category}"))
    
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories"))
    
    await call.message.edit_text("➕ Выберите категорию для добавления:", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("select_cat_"))
async def select_category_for_add(call: types.CallbackQuery):
    await call.answer()
    """Выбрать категорию для добавления"""
    category = call.data.replace("select_cat_", "")
    
    # Показываем кнопки для выбора приоритета
    keyboard = InlineKeyboardMarkup(row_width=3)
    
    # Кнопки с приоритетами от 1 до 10
    buttons = []
    for i in range(1, 11):
        buttons.append(InlineKeyboardButton(f"{i}", callback_data=f"priority_{category}_{i}"))
    
    # Добавляем кнопки по 3 в ряд
    for i in range(0, len(buttons), 3):
        row = buttons[i:i+3]
        keyboard.add(*row)
    
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="add_category"))
    
    await call.message.edit_text(
        f"📝 Выбрана категория: {category}\n\nВыберите приоритет (1 - самый высокий, 10 - самый низкий):",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda call: call.data == "remove_category")
async def remove_category_start(call: types.CallbackQuery):
    await call.answer()
    """Начать удаление категории"""
    categories = db.get_prefer_categories()
    
    if not categories:
        await call.message.edit_text("❌ Нет категорий для удаления.")
        await show_categories_menu(call.message)
        return
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    for category in categories:
        keyboard.add(InlineKeyboardButton(f"❌ {category}", callback_data=f"remove_cat_{category}"))
    
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories"))
    
    await call.message.edit_text("❌ Выберите категорию для удаления:", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("remove_cat_"))
async def remove_category_confirm(call: types.CallbackQuery):
    await call.answer()
    """Подтвердить удаление категории"""
    category = call.data.replace("remove_cat_", "")
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_remove_{category}"),
        InlineKeyboardButton("❌ Отмена", callback_data="back_to_categories")
    )
    
    await call.message.edit_text(f"⚠️ Вы уверены, что хотите удалить категорию '{category}'?", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("confirm_remove_"))
async def confirm_remove_category(call: types.CallbackQuery):
    await call.answer()
    """Подтвердить удаление категории"""
    category = call.data.replace("confirm_remove_", "")
    
    db.remove_prefer_category(category)
    await call.message.edit_text(f"✅ Категория '{category}' удалена!")
    
    # Показываем обновлённый список
    await show_categories_for_message(call.message)

@dp.callback_query_handler(lambda call: call.data == "clear_categories")
async def clear_categories_confirm(call: types.CallbackQuery):
    await call.answer()
    """Подтвердить очистку всех категорий"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("✅ Да, очистить все", callback_data="confirm_clear"),
        InlineKeyboardButton("❌ Отмена", callback_data="back_to_categories")
    )
    
    await call.message.edit_text("⚠️ Вы уверены, что хотите удалить ВСЕ предпочтительные категории?", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data == "confirm_clear")
async def confirm_clear_categories(call: types.CallbackQuery):
    await call.answer()
    """Подтвердить очистку всех категорий"""
    db.clear_prefer_categories()
    await call.message.edit_text("✅ Все предпочтительные категории удалены!")
    
    # Показываем обновлённое меню
    await show_categories_menu(call.message)

@dp.callback_query_handler(lambda call: call.data == "back_to_categories")
async def back_to_categories(call: types.CallbackQuery):
    await call.answer()
    """Вернуться к списку категорий"""
    await show_categories(call)

@dp.callback_query_handler(lambda call: call.data == "back_to_admin_c")
async def back_to_admin(call: types.CallbackQuery):
    await call.answer()
    """Вернуться к главному админ-меню"""
    await admin_categories_menu(call.message)

@dp.callback_query_handler(lambda call: call.data.startswith("priority_"))
async def select_priority(call: types.CallbackQuery):
    await call.answer()
    """Выбрать приоритет для категории"""
    # Парсим данные: priority_категория_приоритет
    data = call.data.replace("priority_", "")
    parts = data.split("_", 1)
    
    if len(parts) != 2:
        await call.message.edit_text("❌ Ошибка при выборе приоритета.")
        return
    
    category = parts[0]
    priority = int(parts[1])
    
    # Добавляем категорию с выбранным приоритетом
    db.add_prefer_category(category, priority)
    
    await call.message.edit_text(f"✅ Категория '{category}' добавлена с приоритетом {priority}!")
    
    # Показываем обновлённый список
    await show_categories_for_message(call.message) 