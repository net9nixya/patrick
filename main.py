import sqlite3
import time
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN, REFERAL_REWARD, BOT_NAME, ADMIN, CHANNEL_LINK, CHAT_LINK, ADMIN_USERNAME, OTZIVI_LINK, VIVODI_LINK, BOT_USERNAME, RULETKA_LINK, RULETKA_LINK2, BONUS_REWARD, DAILY_REWARD, CLICKER_REWARD
from keyboards import start_keyboard, earn_stars_keyboard, profile_keyboard, instruction_keyboard, roulette_keyboard, withdraw_keyboard, admin_confirm_keyboard, top_keyboard, promocode_keyboard, back_menu_keyboard, admin_cmd_keyboard, vizruzka_keyboard, tasks_keyboard, otziv_keyboard

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    stars INTEGER DEFAULT 0,
    last_click INTEGER DEFAULT 0,
    referals INTEGER DEFAULT 0,
    username TEXT,
    admin INTEGER DEFAULT 0,
    activated INTEGER DEFAULT 0,
    withdrawal_request INTEGER DEFAULT 0,
    last_bonus INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS promo_codes (
    code TEXT PRIMARY KEY,
    reward INTEGER,
    uses_left INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS withdraw_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    timestamp INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER,
    title TEXT,
    reward INTEGER,
    active INTEGER DEFAULT 1
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_tasks (
    user_id INTEGER,
    task_id INTEGER,
    status TEXT DEFAULT 'pending', -- 'completed', 'skipped', 'pending'
    PRIMARY KEY (user_id, task_id)
)
""")

conn.commit()

promo_active = set()  # Кто нажал кнопку промокодов
promo_creation = {}   # Для создания новых промокодов админами
promo_deletion = set()
pending_give_stars = {}   # user_id -> True
pending_take_stars = {}   # user_id -> True
task_creation = {}

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    args = message.get_args()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id, stars, referals, activated, username) VALUES (?, 0, 0, 0, ?)", (user_id, username))
        conn.commit()

    # Реферальная система
    if args and args.isdigit() and int(args) != user_id:
        referer_id = int(args)

        cursor.execute("SELECT activated FROM users WHERE user_id = ?", (user_id,))
        ref_user = cursor.fetchone()
        if ref_user and ref_user[0] == 0:
            cursor.execute("UPDATE users SET stars = stars + ?, referals = referals + 1 WHERE user_id = ?", (REFERAL_REWARD, referer_id))
            cursor.execute("UPDATE users SET activated = 1 WHERE user_id = ?", (user_id,))
            conn.commit()

            try:
                await bot.send_message(referer_id, f"🎉 Новый реферал! Вы получили {REFERAL_REWARD} ⭐️")
            except:
                pass

    text = (
        "1️⃣ <b>Получи свою личную ссылку —</b> жми «⭐️\n Заработать звезды»\n"
        "2️⃣ <b>Приглашай друзей — 25000</b>⭐️ за каждого!\n\n"
        "✅ <b>Дополнительно:</b>\n"
        "<blockquote><b>— Ежедневные награды и промокоды</b>\n<b>(Профиль)</b>\n"
        "<b>— Выполняй задания\nКрути рулетку и удвой баланс!</b>\n"
        "<b>— Участвуй в конкурсе на топ</b>\n"
        "<b>— Данный бот создан для тех, у кого\nне получается купить звёзды\nв Telegram Beta.</b></blockquote>\n\n"
        "🔻 <b>Главное меню</b>"
    )

    with open("1патрик с лого (пост лого)_1.mp4", "rb") as video:
        await bot.send_video(
            chat_id=message.chat.id,
            video=video,
            caption=text,
            reply_markup=start_keyboard(),
            parse_mode="HTML"
        )
        
@dp.message_handler(commands=["adm"])
async def admin_command_handler(message: types.Message):
    user_id = message.from_user.id

    if user_id not in ADMIN:
        return

    text = (
        "👑 Здравствуй, администратор Patrick`a. Вот доступные тебе команды:\n"
        "<blockquote>"
        "- <code>создать промокод</code>\n"
        "- <code>удалить промокод</code>\n"
        "- <code>активные промокоды</code>\n"
        "- <code>выдать звезды [ID]</code>\n"
        "- <code>забрать звезды [ID]</code>\n"
        "</blockquote>"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=admin_cmd_keyboard())
    
@dp.callback_query_handler(lambda c: c.data == "vizruzka")
async def handle_vizruzka(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in ADMIN:
        return  # Тихо игнорируем

    # Показываем клавиатуру с действиями выгрузки
    text = "📦 Выгрузка данных. Выберите тип:"
    await callback_query.message.edit_text(
        text,
        reply_markup=vizruzka_keyboard(),
        parse_mode="HTML"
    )
    
@dp.callback_query_handler(lambda c: c.data == "dump_users")
async def handle_dump_users(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ADMIN:
        return

    db_path = "users.db"

    try:
        await bot.send_document(
            chat_id=callback_query.from_user.id,
            document=types.InputFile(db_path),
            caption="📦 Выгрузка базы данных пользователей (users.db)"
        )
        await callback_query.answer("✅ Файл отправлен.")
    except Exception as e:
        print(f"Ошибка при отправке users.db: {e}")
        await callback_query.answer("❌ Ошибка при отправке файла.", show_alert=True)
        
@dp.message_handler(text=["выдать звезды"])
async def give_stars_command(message: types.Message):
    if message.from_user.id not in ADMIN:
        return
    pending_give_stars[message.from_user.id] = True
    await message.answer("✍️ Введите <code>ID</code> пользователя и количество звёзд через пробел:\nПример: <code>123456789 50</code>", parse_mode="HTML")

@dp.message_handler(text=["забрать звезды"])
async def take_stars_command(message: types.Message):
    if message.from_user.id not in ADMIN:
        return
    pending_take_stars[message.from_user.id] = True
    await message.answer("✍️ Введите <code>ID</code> пользователя и сколько звёзд забрать через пробел:\nПример: <code>123456789 25</code>", parse_mode="HTML")

@dp.message_handler(lambda message: message.from_user.id in pending_give_stars or message.from_user.id in pending_take_stars)
async def process_admin_star_change(message: types.Message):
    try:
        parts = message.text.strip().split()
        target_id = int(parts[0])
        amount = float(parts[1])

        if message.from_user.id in pending_give_stars:
            cursor.execute("UPDATE users SET stars = stars + ? WHERE user_id = ?", (amount, target_id))
            conn.commit()
            await message.answer(f"✅ Вы выдали {amount} ⭐️ пользователю {target_id}")
            await bot.send_message(target_id, f"🎁 Вам выдано {amount} ⭐️ администрацией.")
            pending_give_stars.pop(message.from_user.id)

        elif message.from_user.id in pending_take_stars:
            cursor.execute("UPDATE users SET stars = stars - ? WHERE user_id = ?", (amount, target_id))
            conn.commit()
            await message.answer(f"✅ Вы забрали {amount} ⭐️ у пользователя {target_id}")
            await bot.send_message(target_id, f"⛔️ У вас было снято {amount} ⭐️ администрацией.")
            pending_take_stars.pop(message.from_user.id)

    except Exception as e:
        await message.answer(f"❌ Ошибка обработки: {e}")

# Обработчик кнопки "🎁 Ежедневка"
@dp.callback_query_handler(lambda c: c.data == "daily_bonus")
async def daily_bonus_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Получаем пользователя из базы
    cursor.execute("SELECT stars, last_bonus FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    if not user:
        await callback_query.answer("❌ Произошла ошибка. Попробуйте позже.", show_alert=True)
        return

    stars, last_bonus = user
    current_time = int(time.time())

    # Проверяем наличие личной реферальной ссылки в профиле
    try:
        user_info = await bot.get_chat(user_id)
        bio = user_info.bio or ""

        # Формируем ссылку для поиска
        referral_link = f"t.me/{BOT_NAME}?start={user_id}"

        if referral_link not in bio and ("https://" + referral_link) not in bio:
            await callback_query.answer(
                "❌ Сначала поставь свою личную ссылку в описание профиля или измени настройки конфиденциальности",
                show_alert=True
            )
            return
    except Exception as e:
        print(f"Ошибка при проверке описания профиля: {e}")
        await callback_query.answer(
            "❌ Не удалось проверить профиль. Разрешите доступ к вашему описанию или попробуйте позже.",
            show_alert=True
        )
        return

    # Проверка времени последнего бонуса
    if last_bonus and current_time - last_bonus < 86400:  # 24 часа = 86400 секунд
        await callback_query.answer("❌ Бонус можно получить раз в 24 часа!", show_alert=True)
        return

    # Выдаём бонус
    new_stars = stars + {DAILY_REWARD}
    cursor.execute("UPDATE users SET stars = ?, last_bonus = ? WHERE user_id = ?", (new_stars, current_time, user_id))
    conn.commit()

    await callback_query.answer(f"✅ Ты получил(а) ежедневный бонус в размере {DAILY_REWARD} ⭐", show_alert=True)
    
@dp.callback_query_handler(lambda c: c.data.startswith("confirm_withdraw_"))
async def confirm_withdraw_handler(callback_query: types.CallbackQuery):
    data = callback_query.data.split("_")
    user_id = int(data[2])
    amount = int(data[3])

    # Подтверждаем вывод — ничего не возвращаем, просто сбрасываем флаг
    cursor.execute("UPDATE users SET withdrawal_request = 0 WHERE user_id = ?", (user_id,))
    conn.commit()

    await callback_query.answer("✅ Подтверждено: звезды выведены.")

    # Получаем username
    cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    username = user[0] if user else "Без ника"

    # Добавляем запись в историю
    timestamp = int(time.time())
    cursor.execute(
        "INSERT INTO withdraw_history (user_id, amount, timestamp) VALUES (?, ?, ?)",
        (user_id, amount, timestamp)
    )
    conn.commit()

    # Получаем номер этого запроса (ID автоинкремент)
    request_id = cursor.lastrowid

    # Сообщение в канал
    text = f"""
✅ <b>Запрос на вывод №{request_id} </b>

👤 Пользователь: {username} | ID: {user_id}
💫 Количество: {amount}⭐️

🔄 Статус: <b>Подарок отправлен</b> 🎁

<a href="{CHANNEL_LINK}">Основной канал</a> | <a href="{CHAT_LINK}">Чат</a> | <a href="https://t.me/{BOT_USERNAME}">Бот</a>
"""

    await bot.send_message(
        chat_id=VIVODI_LINK,
        text=text,
        disable_web_page_preview=True,
        parse_mode="HTML"
    )

    # Сообщение пользователю
    await bot.send_message(
        user_id,
        f"🎉 <b><a href=\"{ADMIN_USERNAME}\">Патрик</a> отправил тебе твой подарок!</b>\nОставь пожалуйста отзыв и скорее\nначинай зарабатывать ⭐ на новый\nподарок💖",
        reply_markup=otziv_keyboard(),
        parse_mode="HTML"
    )

@dp.callback_query_handler(lambda c: c.data.startswith("reject_withdraw_"))
async def reject_withdraw_handler(callback_query: types.CallbackQuery):
    data = callback_query.data.split("_")
    user_id = int(data[2])
    amount = int(data[3])

    # Отклоняем — возвращаем звезды и сбрасываем флаг
    cursor.execute("UPDATE users SET stars = stars + ?, withdrawal_request = 0 WHERE user_id = ?", (amount, user_id))
    conn.commit()

    await callback_query.answer("❌ Запрос отклонен, звезды возвращены.")
    await bot.send_message(user_id, f"😔 Ваш запрос на вывод {amount} ⭐️ был отклонен.\nЗвезды возвращены на баланс.")

@dp.callback_query_handler(lambda c: c.data == 'earn_stars')
async def earn_stars_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    text = (
        "🎉 <b>Приглашай друзей и получай по 3 ⭐️ от</b>\n<b>Патрика за каждого, кто активирует бота по</b>\n<b>твоей ссылке!</b>\n\n"
        "🔗 <u><b>Твоя личная ссылка</b> (нажми чтобы скопировать)</u>:\n\n"
        f"<code>https://t.me/{BOT_NAME}?start={user_id}</code>\n\n"
        "🚀 <b>Как набрать много переходов по ссылке?</b>\n"
        "<blockquote> • Отправь её друзьям в личные сообщения 👥\n"
        " • Поделись ссылкой в истории в своем ТГ или в своем Telegram канале 📱\n"
        " • Оставь её в комментариях или чатах 🗨\n"
        " • Распространяй ссылку в соцсетях: TikTok, Instagram, WhatsApp и других 🌍</blockquote>"
    )

    with open("Флексит_1.mp4", "rb") as video:
        await bot.send_video(
            chat_id=callback_query.message.chat.id,
            video=video,
            caption=text,
            parse_mode="HTML",
            reply_markup=earn_stars_keyboard(user_id)
        )
        
@dp.callback_query_handler(lambda c: c.data == 'top')
async def top_callback(callback_query: types.CallbackQuery):
    # Получаем топ 3 пользователей за день
    cursor.execute("""
        SELECT user_id, referals FROM users ORDER BY referals DESC LIMIT 3
    """)
    top_users = cursor.fetchall()

    top_text = "<b>🏆 Топ 3 за день:</b>\n\n"
    
    if not top_users or all(referals == 0 for _, referals in top_users):
        top_text = "🏆 <b>Топ 3 за день:</b>\n\n<blockquote><b>- Игроков в топе ещё нету</b> 😪</blockquote>\n\n<b>Попади в топ 3 и получи приз в конце дня:</b>\n<blockquote>- 1ое место + 200⭐️\n- 2ое место + 100⭐️\n- 3е место + 50⭐️</blockquote>\n<b>✨ Ты пока не в топе за этот день.</b>"
    else:
        for i, (user_id, referals) in enumerate(top_users, 1):
            cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            username = user[0] if user else "Неизвестный"

            # Формируем строку для вывода в топ
            top_text += f"🥇 {username} | Друзей: {referals}\n" if i == 1 else \
                        f"🥈 {username} | Друзей: {referals}\n" if i == 2 else \
                        f"🥉 {username} | Друзей: {referals}\n"

        top_text +="""
<b>Попади в топ 3 и получи приз в конце дня:</b>
<blockquote>- 1ое место + 200⭐️
- 2ое место + 100⭐️
- 3е место + 50⭐️</blockquote>"""
    
    user_id = callback_query.from_user.id
    cursor.execute("SELECT referals FROM users WHERE user_id = ?", (user_id,))
    user_referals = cursor.fetchone()[0]

    if user_referals == 0 and not any(user_id == u[0] for u in top_users):
        top_text += "\n✨ <b>Ты пока не в топе за этот день.</b>"

    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=top_text,
        parse_mode="HTML",
        reply_markup=top_keyboard(user_id)
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == 'back_to_menu')
async def back_to_menu(callback_query: types.CallbackQuery):
    await start_command(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == "clicker")
async def clicker_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    cursor.execute("SELECT last_click FROM users WHERE user_id = ?", (user_id,))
    last_click = cursor.fetchone()
    if last_click:
        last_click = last_click[0]
    else:
        last_click = 0

    import time
    current_time = int(time.time())
    cooldown_time = 600

    if current_time - last_click < cooldown_time:
        remaining_time = cooldown_time - (current_time - last_click)
        await callback_query.answer(
            f"⌛ Подожди {remaining_time // 60} мин. {remaining_time % 60} сек. перед следующим кликом",
            show_alert=True
        )
    else:
        cursor.execute("UPDATE users SET last_click = ? WHERE user_id = ?", (current_time, user_id))
        conn.commit()

        cursor.execute("UPDATE users SET stars = stars + ? WHERE user_id = ?", (CLICKER_REWARD, user_id))
        conn.commit()

        await callback_query.answer(f"🌟 Ты получил(а) {CLICKER_REWARD} ⭐!", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == 'profile')
async def profile_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

    text = (
        "✨ <b>Профиль</b>\n"
        "──────────────\n"
        f"👤 <b>Имя: {callback_query.from_user.username}</b>\n"
        f"🆔 <b>ID: {callback_query.from_user.id}</b>\n"
        "──────────────\n"
        f"👥 Всего друзей: {user[3]}\n"
        f"✅ Активировали бота: {user[6]}\n"
        f"💰 Баланс: {user[1]} ⭐️ \n\n"
        "⁉️ Как получить ежедневный бонус?\n"
        f"<blockquote>Поставь свою личную ссылку на бота в описание своего тг аккаунта, и получай за это +{BONUS_REWARD} ⭐️ каждый день.</blockquote>\n\n"
        "⬇️  <i>Используй кнопки ниже, чтобы ввести промокод, или получить ежедневный бонус.</i>"
    )

    with open("1патрик с лого (пост профиль).mp4", "rb") as video:
        await bot.send_video(
            chat_id=callback_query.message.chat.id,
            video=video,
            caption=text,
            reply_markup=profile_keyboard(),
            parse_mode="HTML"
        )

# Обработчик кнопки "📋 Задания"
@dp.callback_query_handler(lambda c: c.data == 'tasks')
async def tasks_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    # Получаем активные задания, которые пользователь еще не выполнил и не пропустил
    cursor.execute("""
        SELECT tasks.task_id, tasks.title, tasks.reward, tasks.chat_id 
        FROM tasks 
        LEFT JOIN user_tasks ON tasks.task_id = user_tasks.task_id AND user_tasks.user_id = ?
        WHERE tasks.active = 1 AND (user_tasks.status IS NULL OR user_tasks.status = 'pending')
    """, (user_id,))
    tasks = cursor.fetchall()

    if not tasks:
        text = "🎉 <b>Все задания выполнены или пропущены!</b>"
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=text,
            reply_markup=back_menu_keyboard(),
            parse_mode="HTML"
        )
        await callback_query.answer()
        return

    # Формируем текст с заданиями
    text = "📋 <b>Доступные задания:</b>\n\n"
    for task_id, title, reward, chat_id in tasks:
        text += f"🔹 <b>{title}</b>: {reward} ⭐️\n"

    # Отправляем первое задание с клавиатурой
    first_task = tasks[0]
    task_id, title, reward, chat_id = first_task
    text = f"📋 <b>Задание:</b> {title}\n🎁 <b>Награда:</b> {reward} ⭐️\n\nПодпишись на канал/чат и проверь подписку!"

    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=text,
        reply_markup=tasks_keyboard(task_id, chat_id),
        parse_mode="HTML"
    )
    await callback_query.answer()

# Обработчик проверки подписки
# Обработчик проверки подписки
@dp.callback_query_handler(lambda c: c.data.startswith('check_subscription_'))
async def check_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    task_id = int(callback_query.data.split('_')[2])
    chat_id = int(callback_query.data.split('_')[3])

    try:
        # Проверяем, подписан ли пользователь
        member = await bot.get_chat_member(chat_id, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            # Проверяем, не выполнено ли задание ранее
            cursor.execute("SELECT status FROM user_tasks WHERE user_id = ? AND task_id = ?", (user_id, task_id))
            status = cursor.fetchone()
            if status and status[0] == 'completed':
                await callback_query.answer("❌ Вы уже выполнили это задание!", show_alert=True)
                return

            # Получаем текущий баланс
            cursor.execute("SELECT stars FROM users WHERE user_id = ?", (user_id,))
            current_stars = cursor.fetchone()[0] or 0  # Если None, ставим 0
            # Получаем награду за задание
            cursor.execute("SELECT reward FROM tasks WHERE task_id = ?", (task_id,))
            reward = cursor.fetchone()[0]
            # Обновляем баланс, добавляя награду
            new_stars = current_stars + reward
            cursor.execute("UPDATE users SET stars = ? WHERE user_id = ?", (new_stars, user_id))
            cursor.execute("INSERT OR REPLACE INTO user_tasks (user_id, task_id, status) VALUES (?, ?, ?)", 
                          (user_id, task_id, 'completed'))
            conn.commit()

            await callback_query.answer(f"✅ Задание выполнено! Вы получили {reward} ⭐️. Новый баланс: {new_stars} ⭐️", show_alert=True)
            # Повторно вызываем tasks_callback для показа следующего задания
            await tasks_callback(callback_query)
        else:
            await callback_query.answer("❌ Вы не подписаны на канал/чат! Подпишитесь и попробуйте снова.", show_alert=True)
    except Exception as e:
        print(f"Ошибка при проверке подписки: {e}")
        await callback_query.answer("❌ Ошибка при проверке подписки. Попробуйте позже.", show_alert=True)

# Обработчик пропуска задания
@dp.callback_query_handler(lambda c: c.data.startswith('skip_task_'))
async def skip_task(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    task_id = int(callback_query.data.split('_')[2])

    # Помечаем задание как пропущенное
    cursor.execute("INSERT OR REPLACE INTO user_tasks (user_id, task_id, status) VALUES (?, ?, ?)", 
                  (user_id, task_id, 'skipped'))
    conn.commit()

    await callback_query.answer("↗️ Задание пропущено и больше не появится.", show_alert=True)
    # Повторно вызываем tasks_callback для показа следующего задания
    await tasks_callback(callback_query)

# Команда создания задания для админов
@dp.message_handler(commands=['create_task'])
async def create_task_command(message: types.Message):
    user_id = message.from_user.id
    print(f"Received /create_task from user_id: {user_id}")  # Отладка
    if user_id not in ADMIN:
        print(f"User {user_id} is not admin")  # Отладка
        await message.answer("❌ У вас нет прав для создания заданий.", reply_markup=back_menu_keyboard())
        return

    print(f"Starting task creation for user_id: {user_id}")  # Отладка
    task_creation[user_id] = {"step": 1}
    await message.answer("✅ Введите супер ID чата/канала (пример: -1234567890000):", parse_mode="HTML")

# Обработчик ввода данных для создания задания
@dp.message_handler(lambda message: message.from_user.id in task_creation)
async def process_task_creation(message: types.Message):
    user_id = message.from_user.id
    data = task_creation[user_id]

    if data["step"] == 1:
        try:
            chat_id = int(message.text.strip())
            data["chat_id"] = chat_id
            data["step"] = 2
            await message.answer("📝 Введите название задания:")
        except ValueError:
            await message.answer("❌ Введите корректный ID чата/канала (пример: -1234567890000).")
    elif data["step"] == 2:
        data["title"] = message.text.strip()
        data["step"] = 3
        await message.answer("⭐ Введите количество звёзд за выполнение задания:")
    elif data["step"] == 3:
        try:
            reward = int(message.text.strip())
            cursor.execute("INSERT INTO tasks (chat_id, title, reward, active) VALUES (?, ?, ?, 1)",
                          (data["chat_id"], data["title"], reward))
            conn.commit()
            await message.answer(f"✅ Задание <b>{data['title']}</b> создано!\n🎯 Награда: {reward} ⭐ | Чат/канал: {data['chat_id']}", 
                               parse_mode="HTML", reply_markup=back_menu_keyboard())
            task_creation.pop(user_id)
        except ValueError:
            await message.answer("❌ Введите число звёзд.")
    
# Рулетка
@dp.callback_query_handler(lambda c: c.data == 'roulette')
async def roulette_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    cursor.execute("SELECT stars FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        stars_balance = user[0]
    else:
        stars_balance = 0

    text = (
        "🎰 <u><b>Крути рулетку и удвой свой баланс!</b></u>\n\n"
        f"📊 <b>Онлайн статистика выигрышей:</b>\n{RULETKA_LINK2}\n\n"
        f"💰 <b>Баланс:</b> {stars_balance} ⭐️\n\n"
        "⬇️ <b>Выбери ставку:</b>\n\n"
    )

    with open("0. Мини Игры - Рулетка.mp4", "rb") as video:
        await bot.send_video(
            chat_id=callback_query.message.chat.id,
            video=video,
            caption=text,
            reply_markup=roulette_keyboard(),
            parse_mode="HTML"
        )

    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('bet_'))
async def handle_bet(callback_query: types.CallbackQuery):
    # Сразу отвечаем Telegram, без текста
    await callback_query.answer()  # Без текста, просто чтобы Telegram не ждал

    user_id = callback_query.from_user.id
    bet_amount_str = callback_query.data.split('_')[1]

    try:
        bet_amount = float(bet_amount_str)
    except ValueError:
        await bot.send_message(user_id, "❌ Ошибка ставки.")  # в чат, не alert
        return

    cursor.execute("SELECT stars, username FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        balance, username = result
    else:
        balance = 0
        username = "Без ника"

    if balance < bet_amount:
        await bot.send_message(user_id, "❌ Недостаточно звёзд для ставки!")  # в чат, не alert
        return

    import random
    chance = random.randint(1, 100)
    won = chance <= 35

    if won:
        winnings = bet_amount * 2
        new_balance = balance + winnings
        result_text = (
            f"🎉 Поздравляю, ты выиграл(а): {winnings} звёзд⭐\n"
            "Отличный результат - не останавливайся, попробуй ещё раз! 🚀"
        )
    else:
        winnings = 0
        new_balance = balance - bet_amount
        result_text = (
            "😕 Неудача, не расстраивайся,\n"
            "надеюсь в следующий раз тебе повезет 🙏"
        )

    cursor.execute("UPDATE users SET stars = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()

    if won:
        ruletka_text = f"""
🎉 Поздравляем! 🏆

Пользователь {username} (ID: {user_id}) 
выиграл {winnings}⭐️ на ставке {bet_amount}⭐️ 🎲

🚀 Просто потрясающий выигрыш! 🏆🌟 🎉
"""
        await bot.send_message(
            chat_id=RULETKA_LINK,
            text=ruletka_text,
            disable_web_page_preview=True
        )

    # Обновляем интерфейс
    text = (
        f"🎰 <u><b>Крути рулетку и удвой свой баланс!</b></u>\n\n"
        f"📊 <b>Онлайн статистика выигрышей:</b>\n{RULETKA_LINK2}\n\n"
        f"💰 <b>Баланс:</b> {new_balance} ⭐️\n\n"
        "⬇️ <b>Выбери ставку:</b>\n\n"
    )

    with open("0. Мини Игры - Рулетка.mp4", "rb") as video:
        await bot.send_video(
            chat_id=callback_query.message.chat.id,
            video=video,
            caption=text,
            reply_markup=roulette_keyboard(),
            parse_mode="HTML"
        )

    # И только теперь — отправляем итоговое сообщение (через обычный message, не alert)
    await bot.send_message(callback_query.message.chat.id, result_text)
        
@dp.callback_query_handler(lambda c: c.data == "instruction")
async def instruction_callback(callback_query: types.CallbackQuery):
    text = (
        "📌 <b> Как набрать много переходов по\nссылке?</b>\n"
        "<blockquote> • Отправь её друзьям в личные\nсообщения 🧍‍♂️🧍‍♀️\n"
        "• Поделись ссылкой в истории и в своем ТГ\nили в Telegram-канале 📣\n"
        "• Оставь её в комментариях или чатах 🗨️\n"
        "• Распространяй ссылку в соцсетях: TikTok,\nInstagram, WhatsApp и других 🌍</blockquote>\n\n"
        "🤩 <b>Способы, которыми можно заработать\nдо 1000 звёзд в день:</b>\n\n"
        "1️⃣ <b>Первый способ:</b>\n"
        "<blockquote>1. Заходим в TikTok или Лайк\n"
        "2. Ищем видео по запросам: звёзды\nтелеграм, подарки телеграм, тг старсы и\nт.п.\n"
        "3. Оставляем в комментариях текст типа:\n<i>Дарю подарки/звезды, пишите в тг\n@вашюзер</i>\n"
        "4. Отправляете свою личную ссылку тем,\nкто пишет\n"
        "5. Ждём и выводим звезды 💰</blockquote>\n\n"
        "2️⃣ <b>Второй способ:</b>\n"
        "<blockquote>1. Заходим в бот знакомств\n@leomatchbot\n"
        "2. Делаем анкету женского пола\n"
        "3. Лайкаем всех подряд и параллельно\nждём пока нас пролайкают 💞\n"
        "4. Переходим со всеми в ЛС и пишем:\n<i>Привет, помоги мне пожалуйста\nзаработать звёзды. Перейди и\nактивируй бота по моей ссылке:</i> <b>«твоя\n ссылка»</b>\n"
        "5. Ждём и выводим звёзды 🌟</blockquote>\n\n"
        "❗️<b>Ответы на часто задаваемые вопросы</b>\n👉 ТЫК"
    )

    with open("патрик думает.mp4", "rb") as video:
        await bot.send_video(
            chat_id=callback_query.message.chat.id,
            video=video,
            caption=text,
            reply_markup=instruction_keyboard(),
            parse_mode="HTML"
        )

@dp.callback_query_handler(lambda c: c.data == 'withdraw')
async def withdraw_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    cursor.execute("SELECT stars, referals FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return

    stars, referals = user

    text = (
        f"💰<b>Баланс:</b> {stars} ⭐️\n\n"
        f"‼️<b>Для вывода требуется:</b>\n"
        f"— минимум 5 приглашенных друзей, активировавших бота\n"
        f"— Быть подписанным на наш <a href=\"{CHANNEL_LINK}\">канал</a>\n\n"
        f"<blockquote>✅ Вывод в течении 24-х часов.</blockquote>\n\n"
        f"<b>Выбери количество звезд и подарок, которым ты хочешь их получить:</b>"
    )

    with open("IMG_2673.MP4", "rb") as video:
        await bot.send_video(
            chat_id=callback_query.message.chat.id,
            video=video,
            caption=text,
            reply_markup=withdraw_keyboard(),
            parse_mode="HTML"
        )
  
  # ПРОМОКОДЫ
        
@dp.callback_query_handler(lambda c: c.data == 'promo_code')
async def promo_code_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    promo_active.add(user_id)

    text = (
        "<i>✨ Для получения звезд на твой баланс введи промокод: </i>\n"
        f"<i>Найти промокоды можно в <a href=\"{CHANNEL_LINK}\">канале</a> и <a href=\"{CHAT_LINK}\">чате</a>.</i>"
    )

    with open("IMG_2669.MP4", "rb") as video:
        await bot.send_video(
            chat_id=callback_query.message.chat.id,
            video=video,
            caption=text,
            reply_markup=promocode_keyboard(),
            parse_mode="HTML"
        )

    await callback_query.answer()

@dp.message_handler(lambda message: message.from_user.id in promo_active)
async def handle_promo_code(message: types.Message):
    user_id = message.from_user.id
    code = message.text.strip()

    # Проверяем, активировал ли уже пользователь этот промокод
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS promo_activations (
        user_id INTEGER,
        code TEXT,
        PRIMARY KEY (user_id, code)
    )
    """)
    conn.commit()

    # Проверка, активировал ли уже этот код
    cursor.execute("SELECT 1 FROM promo_activations WHERE user_id = ? AND code = ?", (user_id, code))
    already_activated = cursor.fetchone()

    if already_activated:
        await message.answer("❌ Вы уже использовали этот промокод.", reply_markup=back_menu_keyboard())
        promo_active.discard(user_id)
        return

    # Проверка, существует ли промокод
    cursor.execute("SELECT reward, uses_left FROM promo_codes WHERE code = ?", (code,))
    result = cursor.fetchone()

    if result:
        reward, uses_left = result
        if uses_left > 0:
            # Обновляем звезды пользователю
            cursor.execute("UPDATE users SET stars = stars + ? WHERE user_id = ?", (reward, user_id))
            # Уменьшаем количество активаций
            cursor.execute("UPDATE promo_codes SET uses_left = uses_left - 1 WHERE code = ?", (code,))
            # Запоминаем, что пользователь использовал промокод
            cursor.execute("INSERT INTO promo_activations (user_id, code) VALUES (?, ?)", (user_id, code))
            conn.commit()

            await message.answer(f"✅ Промокод успешно активирован!\nТебе начислено: {reward} ⭐️!")
        else:
            await message.answer(
                "❌ Промокод не действителен или закончились использования",
                reply_markup=back_menu_keyboard()
            )
    else:
        await message.answer(
            "❌ Промокод не действителен или закончились использования",
            reply_markup=back_menu_keyboard()
        )

    promo_active.discard(user_id)
    
@dp.message_handler(text=['удалить промокод'])
async def delete_promo(message: types.Message):
    if message.from_user.id not in ADMIN:
        await message.answer("❌ У вас нет прав для удаления промокодов.", reply_markup=back_menu_keyboard())
        return

    # Спрашиваем, какой промокод удалить
    await message.answer("Введите название промокода, который хотите удалить:")

    # Помечаем пользователя, чтобы обработать его следующий ввод
    promo_deletion.add(message.from_user.id)

@dp.message_handler(lambda message: message.from_user.id in promo_deletion)
async def process_delete_promo(message: types.Message):
    user_id = message.from_user.id
    code_to_delete = message.text.strip()

    cursor.execute("SELECT code FROM promo_codes WHERE code = ?", (code_to_delete,))
    promo = cursor.fetchone()

    if promo:
        cursor.execute("DELETE FROM promo_codes WHERE code = ?", (code_to_delete,))
        cursor.execute("DELETE FROM promo_activations WHERE code = ?", (code_to_delete,))
        conn.commit()
        await message.answer(f"✅ Промокод <b>{code_to_delete}</b> успешно удалён!", reply_markup=back_menu_keyboard(), parse_mode="HTML")
    else:
        await message.answer("❌ Промокод не найден.", reply_markup=back_menu_keyboard())

    promo_deletion.discard(user_id)

@dp.message_handler(text=['создать промокод'])
async def create_promo(message: types.Message):
    if message.from_user.id not in ADMIN:
        await message.answer("❌ У вас нет прав для создания промокодов.", reply_markup=back_menu_keyboard())
        return

    promo_creation[message.from_user.id] = {"step": 1}
    await message.answer("🎉 Введите название нового промокода:")

@dp.message_handler(lambda message: message.from_user.id in promo_creation)
async def process_promo_creation(message: types.Message):
    user_id = message.from_user.id
    data = promo_creation[user_id]

    if data["step"] == 1:
        data["code"] = message.text.strip()
        data["step"] = 2
        await message.answer("🚀 Введите сколько активаций будет у промокода:")
    elif data["step"] == 2:
        try:
            data["uses_left"] = int(message.text.strip())
            data["step"] = 3
            await message.answer("⭐ Введите сколько звёзд будет давать промокод:")
        except ValueError:
            await message.answer("❌ Введите число активаций.")
    elif data["step"] == 3:
        try:
            reward = int(message.text.strip())
            # Создание промокода в БД
            cursor.execute("INSERT OR REPLACE INTO promo_codes (code, reward, uses_left) VALUES (?, ?, ?)",
                           (data["code"], reward, data["uses_left"]))
            conn.commit()

            await message.answer(f"✅ Промокод <b>{data['code']}</b> успешно создан!\n🎯 Награда: {reward} ⭐ | Активаций: {data['uses_left']}", parse_mode="HTML", reply_markup=back_menu_keyboard())
            promo_creation.pop(user_id)
        except ValueError:
            await message.answer("❌ Введите число звёзд.")

@dp.message_handler(text=['активные промокоды'])
async def list_promo(message: types.Message):
    if message.from_user.id not in ADMIN:
        await message.answer("❌ У вас нет прав для просмотра промокодов.", reply_markup=back_menu_keyboard())
        return

    cursor.execute("SELECT code, reward, uses_left FROM promo_codes")
    promos = cursor.fetchall()

    if not promos:
        await message.answer("❌ Нет активных промокодов.", reply_markup=back_menu_keyboard())
        return

    text = "<b>⭐ Список промокодов:</b>\n\n"
    for code, reward, uses_left in promos:
        text += f"🔹 {code} — {reward} ⭐ | Осталось активаций: {uses_left}\n"

    await message.answer(text, parse_mode="HTML")

#________________________________________________________________________________________________________________________

@dp.callback_query_handler(lambda c: c.data.startswith('withdraw_'))
async def process_withdraw(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username or "Без ника"
    data = callback_query.data.split('_')
    amount_str = data[1]
    try:
        amount = int(amount_str)
    except ValueError:
        amount = 1700

    cursor.execute("SELECT stars, referals, withdrawal_request FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return

    stars, referals, withdrawal_request = user

    if withdrawal_request:
        await callback_query.answer(
            "❌ Вы уже отправили запрос на вывод. Пожалуйста, дождитесь его одобрения.",
            show_alert=True
        )
        return

    if referals < 5:
        await callback_query.answer(
            "❌ Для вывода необходимо пригласить минимум 5 друзей, которые активировали бота!",
            show_alert=True
        )
        return

    if stars < amount:
        await callback_query.answer(
            f"❌ У вас недостаточно звёзд для этого вывода!",
            show_alert=True
        )
        return

    new_stars = stars - amount
    cursor.execute("UPDATE users SET stars = ?, withdrawal_request = 1 WHERE user_id = ?", (new_stars, user_id))
    conn.commit()

    text = (
        f"<b>@{username}</b> отправил подтверждение на вывод своих звёзд!\n\n"
        f"💎 <b>Сколько нужно вывести:</b> {amount} ⭐️"
    )

    for admin_id in ADMIN:
        await bot.send_message(
            chat_id=admin_id,
            text=text,
            reply_markup=admin_confirm_keyboard(user_id, amount),
            parse_mode="HTML"
        )

    await callback_query.answer(
        "✅ Заявка на вывод отправлена администратору!",
        show_alert=True
    )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
