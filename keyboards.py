from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_NAME, OTZIVI_LINK

def start_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("🌟 Кликер", callback_data="clicker"),
    )
    keyboard.add(
        InlineKeyboardButton("⭐ Заработать звёзды", callback_data="earn_stars"), 
    )
    keyboard.add(
        InlineKeyboardButton("👤 Профиль", callback_data="profile"),
        InlineKeyboardButton("💰 Вывод звёзд", callback_data="withdraw"),
    )
    keyboard.add(
        InlineKeyboardButton("📋 Задания", callback_data="tasks"),
        InlineKeyboardButton("🎰 Рулетка", callback_data="roulette"),
    )
    keyboard.add(
        InlineKeyboardButton("🚀 Буст", callback_data="boost"),
        InlineKeyboardButton("📚 Инструкция", callback_data="instruction"),
    )
    keyboard.add(
        InlineKeyboardButton("🏆 Топ", callback_data="top"),
        InlineKeyboardButton("📧 Отзывы", url=f"{OTZIVI_LINK}")
    )

    return keyboard

def profile_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🎫 Промокод", callback_data="promo_code"),
        InlineKeyboardButton("🎁 Ежедневка", callback_data="daily_bonus"),
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu"),
    )
    return keyboard

# Клавиатура для кнопки "⭐ Заработать звёзды"
def earn_stars_keyboard(user_id):
    # Создаем инлайн кнопку для отправки ссылки
    referral_link = f"https://t.me/{BOT_NAME}?start={user_id}"
    send_to_friends_button = InlineKeyboardButton(
        text="📎 Отправить друзьям", 
        url=f"tg://msg_url?url={referral_link}&text="
    )
    # Кнопка для возврата в меню
    back_button = InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_menu")

    # Создаем клавиатуру с этими кнопками
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(send_to_friends_button, back_button)
    
    return keyboard

def instruction_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu"),
    )
    return keyboard

def promocode_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu"),
    )
    return keyboard

def roulette_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton("0.5⭐️", callback_data="bet_0.5"),
        InlineKeyboardButton("1⭐️", callback_data="bet_1"),
        InlineKeyboardButton("2⭐️", callback_data="bet_2"),
        InlineKeyboardButton("3⭐️", callback_data="bet_3"),
        InlineKeyboardButton("5⭐️", callback_data="bet_5"),
        InlineKeyboardButton("10⭐️", callback_data="bet_10"),
        InlineKeyboardButton("50⭐️", callback_data="bet_50"),
        InlineKeyboardButton("100⭐️", callback_data="bet_100"),
        InlineKeyboardButton("500⭐️", callback_data="bet_500"),
        InlineKeyboardButton("1000⭐️", callback_data="bet_1000"),
        InlineKeyboardButton("2500⭐️", callback_data="bet_2500"),
        InlineKeyboardButton("5000⭐️", callback_data="bet_5000"),
        InlineKeyboardButton("10000⭐️", callback_data="bet_10000"),
    )
    keyboard.add(
        InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu")
    )
    return keyboard

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def withdraw_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("15⭐ (🧸)", callback_data="withdraw_15_1"),
            InlineKeyboardButton("15⭐ (💝)", callback_data="withdraw_15_2"),
        ],
        [
            InlineKeyboardButton("25⭐ (🌹)", callback_data="withdraw_25_1"),
            InlineKeyboardButton("25⭐ (🎁)", callback_data="withdraw_25_2"),
        ],
        [
            InlineKeyboardButton("50⭐ (🍾)", callback_data="withdraw_50_1"),
            InlineKeyboardButton("50⭐ (💐)", callback_data="withdraw_50_2"),
        ],
        [
            InlineKeyboardButton("50⭐ (🚀)", callback_data="withdraw_50_3"),
            InlineKeyboardButton("50⭐ (🎂)", callback_data="withdraw_50_4"),
        ],
        [
            InlineKeyboardButton("100⭐ (🏆)", callback_data="withdraw_100_1"),
            InlineKeyboardButton("100⭐ (💍)", callback_data="withdraw_100_2"),
        ],
        [
            InlineKeyboardButton("100⭐ (💎)", callback_data="withdraw_100_3"),
        ],
        [
            InlineKeyboardButton("Telegram Premium 6мес. (1700⭐️)", callback_data="withdraw_premium"),
        ],
    ])
    return keyboard

def admin_confirm_keyboard(user_id, amount):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("✅ Принять", callback_data=f"confirm_withdraw_{user_id}_{amount}"),
            InlineKeyboardButton("❌ Отказ", callback_data=f"reject_withdraw_{user_id}_{amount}"),
            InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu"),
        ]
    ])
    return keyboard

def top_keyboard(user_id):
    # Создание клавиатуры
    keyboard = InlineKeyboardMarkup()
    
    # Добавление кнопки назад в главное меню
    keyboard.add(InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu"))
    keyboard.add(InlineKeyboardButton(f"❌ Не обращай внимания {user_id}", callback_data=f"user_{user_id}"))
    
    return keyboard

def back_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu"),
    )
    return keyboard

def admin_cmd_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("Выгрузка", callback_data=f"vizruzka"),
            InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_to_menu"),
        ]
    ])
    return keyboard

def vizruzka_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("👤 Пользователи", callback_data="dump_users"),
            InlineKeyboardButton("⭐ Баланс", callback_data="dump_stars"),
        ],
        [
            InlineKeyboardButton("⬅️ Назад", callback_data="adm_back")
        ]
    ])
    return keyboard
