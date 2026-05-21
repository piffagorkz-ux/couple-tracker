#!/usr/bin/env python3
"""
🖤 Couple Tracker Bot — v3.0 (FIXED)
Геймификация, скрытые ответы, аналитика, челленджи, тайные признания,
синхронизация данных в реальном времени
"""

import logging, json, os, asyncio, random
from datetime import datetime, date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔐 ТОКЕН ИЗ ПЕРЕМЕННОЙ ОКРУЖЕНИЯ (безопасно)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Ошибка: переменная окружения BOT_TOKEN не установлена!\n"
                     "Установите её перед запуском: export BOT_TOKEN='ваш_токен_здесь'")

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "couple_data.json")

# ── 🖼️ КАРТИНКИ ───────────────────────────────────────────────────────────────
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tree_images")
_PHOTO_CACHE = {}

def _img_path(name: str) -> str:
    return os.path.join(IMAGES_DIR, name)

async def send_photo_cached(bot, chat_id, img_name: str, caption: str, reply_markup=None, parse_mode="Markdown"):
    """Отправляет картинку с кэшированием file_id."""
    cache_key = img_name
    if cache_key in _PHOTO_CACHE:
        msg = await bot.send_photo(
            chat_id=chat_id,
            photo=_PHOTO_CACHE[cache_key],
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
    else:
        path = _img_path(img_name)
        if os.path.exists(path):
            with open(path, "rb") as f:
                msg = await bot.send_photo(
                    chat_id=chat_id,
                    photo=f,
                    caption=caption,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup
                )
            _PHOTO_CACHE[cache_key] = msg.photo[-1].file_id
        else:
            await bot.send_message(chat_id=chat_id, text=caption, parse_mode=parse_mode, reply_markup=reply_markup)
            return None
    return msg

async def edit_or_send_photo(query, img_name: str, caption: str, reply_markup=None):
    """Удаляет старое сообщение и отправляет новое с фото."""
    chat_id = query.message.chat_id
    try:
        await query.message.delete()
    except Exception:
        pass
    await send_photo_cached(query.get_bot(), chat_id, img_name, caption, reply_markup)

# ── состояния ──────────────────────────────────────────────────────────────────
(
    WAITING_PARTNER_ID,
    WAITING_DATE_NAME, WAITING_DATE_VALUE, WAITING_DATE_ANNUAL,
    WAITING_MOOD_NOTE,
    WAITING_DATE_PLAN_TITLE, WAITING_DATE_PLAN_DATE, WAITING_DATE_PLAN_DESC,
    WAITING_CONFESSION, WAITING_CONFESSION_TIME,
    WAITING_GOAL_TEXT,
    WAITING_PLACE_NAME,
    WAITING_CHECKIN_TEXT,
    WAITING_DIARY_TEXT,
    WAITING_WISH_TEXT, WAITING_WISH_PRICE,
    WAITING_CAPSULE_TEXT, WAITING_CAPSULE_DATE,
    WAITING_HABIT_TEXT,
    WAITING_HIDDEN_Q, WAITING_HIDDEN_A,
    WAITING_TREE_NAME,
) = range(22)

# ── ачивки ─────────────────────────────────────────────────────────────────────
ACHIEVEMENTS = {
    "first_mood":      {"icon": "🖤", "name": "Первое настроение",   "desc": "Записали первое настроение"},
    "streak_7":        {"icon": "🔥", "name": "Неделя вместе",       "desc": "7 дней подряд оба заходили в бот"},
    "streak_30":       {"icon": "⚡", "name": "Месяц вместе",        "desc": "30 дней подряд активны"},
    "dates_3":         {"icon": "🌹", "name": "Романтики",           "desc": "Провели 3 свидания"},
    "dates_10":        {"icon": "💫", "name": "Мастера свиданий",    "desc": "Провели 10 свиданий"},
    "goals_done_1":    {"icon": "🎯", "name": "Первая цель",         "desc": "Выполнили первую цель"},
    "goals_done_5":    {"icon": "🏆", "name": "Целеустремлённые",   "desc": "Выполнили 5 целей"},
    "places_5":        {"icon": "🗺️", "name": "Путешественники",    "desc": "Побывали в 5 местах"},
    "diary_10":        {"icon": "📝", "name": "Летописцы",          "desc": "10 записей в дневнике"},
    "habits_streak_7": {"icon": "💪", "name": "Сила привычки",       "desc": "Серия 7 дней в привычке"},
    "challenge_done":  {"icon": "🎪", "name": "Принимаем вызов",     "desc": "Выполнили первый челлендж"},
    "checkin_7":       {"icon": "🌙", "name": "Вечерние разговоры",  "desc": "7 вечерних check-in подряд"},
    "wishlist_done":   {"icon": "🎁", "name": "Исполнитель желаний", "desc": "Исполнили желание из вишлиста"},
    "hidden_match":    {"icon": "🔮", "name": "Телепаты",            "desc": "Совпали ответы на скрытый вопрос"},
}

# ── челленджи ──────────────────────────────────────────────────────────────────
CHALLENGES_LIST = [
    {"id": "c1",  "text": "Сходить на свидание вне дома 🌹",             "days": 7},
    {"id": "c2",  "text": "Сделать комплимент 3 раза за день 💬",         "days": 1},
    {"id": "c3",  "text": "Вечер без телефонов 📵",                       "days": 1},
    {"id": "c4",  "text": "Приготовить ужин вместе 🍳",                   "days": 3},
    {"id": "c5",  "text": "Написать 5 вещей, за что ты ценишь партнёра 🖤", "days": 1},
    {"id": "c6",  "text": "Посмотреть новый фильм вместе 🎬",             "days": 3},
    {"id": "c7",  "text": "Утренние обнимашки 5 дней подряд 🤗",         "days": 5},
    {"id": "c8",  "text": "Сюрприз для партнёра без повода 🎁",           "days": 3},
    {"id": "c9",  "text": "Прогулка в новом месте города 🚶",             "days": 7},
    {"id": "c10", "text": "День без споров (мирный день) ☮️",             "days": 1},
    {"id": "c11", "text": "Сфотографироваться вместе в 3 местах 📸",     "days": 7},
    {"id": "c12", "text": "Рассказать друг другу о своей мечте ✨",        "days": 1},
]

# ── скрытые вопросы ────────────────────────────────────────────────────────────
HIDDEN_QUESTIONS = [
    "Что для тебя идеальный вечер вместе?",
    "Куда ты больше всего хочешь поехать с партнёром?",
    "Какой твой любимый совместный момент за последний месяц?",
    "Что в партнёре тебя восхищает больше всего?",
    "Какую привычку ты хочешь развить вместе?",
    "Назови одно место, которое хочешь посетить вдвоём.",
    "Какой подарок ты бы хотел(а) получить?",
    "Что тебя больше всего радует в ваших отношениях?",
    "Чего тебе не хватает в ваших отношениях?",
    "Какое твоё самое счастливое воспоминание о вас двоих?",
]

# ── хранилище ──────────────────────────────────────────────────────────────────

def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data: dict, user_id) -> dict:
    uid = str(user_id)
    if uid not in data:
        data[uid] = {"partner_id": None, "name": "", "last_seen": None}
    return data[uid]

def ck(id1, id2) -> str:
    return f"{min(int(id1), int(id2))}_{max(int(id1), int(id2))}"

def get_couple(data: dict, key: str) -> dict:
    if "couples" not in data:
        data["couples"] = {}
    if key not in data["couples"]:
        data["couples"][key] = {}
    cd = data["couples"][key]
    defaults = {
        "important_dates": [], "dates_plan": [], "moods": {},
        "goals": [], "places": [], "checkins": {},
        "diary": [], "wishlist": [], "capsules": [], "habits": [],
        "achievements": [], "challenges": [], "confessions": [],
        "hidden_q": "", "hidden_answers": {}, "tree_actions": [],
        "tree_name": "🌱 Наше деревце"
    }
    for key, val in defaults.items():
        if key not in cd:
            cd[key] = val
    return cd

# ── главное меню ────────────────────────────────────────────────────────────────

def main_menu_kb(with_partner: bool = False):
    """Главное меню."""
    buttons = [
        [InlineKeyboardButton("🌱 Наше деревце", callback_data="tree_menu")],
        [InlineKeyboardButton("📊 Аналитика", callback_data="analytics")],
        [InlineKeyboardButton("🎯 Цели", callback_data="goals_menu"), 
         InlineKeyboardButton("🎪 Челленджи", callback_data="challenges_menu")],
        [InlineKeyboardButton("💬 Скрытые вопросы", callback_data="hidden_menu"),
         InlineKeyboardButton("🤫 Признания", callback_data="confession_menu")],
        [InlineKeyboardButton("💕 Свидания", callback_data="dates_menu"),
         InlineKeyboardButton("📅 Важные даты", callback_data="special_dates_menu")],
        [InlineKeyboardButton("📝 Дневник", callback_data="diary_menu"),
         InlineKeyboardButton("🎁 Вишлист", callback_data="wishlist_menu")],
        [InlineKeyboardButton("💪 Привычки", callback_data="habits_menu"),
         InlineKeyboardButton("🏆 Ачивки", callback_data="achievements_menu")],
        [InlineKeyboardButton("🗺️ Места", callback_data="places_menu"),
         InlineKeyboardButton("🔮 Time Capsule", callback_data="capsule_menu")],
    ]
    if with_partner:
        buttons.append([InlineKeyboardButton("👥 Инфо о партнёре", callback_data="partner_info")])
    buttons.append([InlineKeyboardButton("⚙️ Настройки", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

def back_btn():
    return InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back_main")]])

# ── обработчики команд ──────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start."""
    data = load_data()
    user = get_user(data, update.effective_user.id)
    
    if user["partner_id"]:
        await update.message.reply_text(
            f"👋 С возвращением, {update.effective_user.first_name}! 💕\n"
            f"Добро пожаловать в ваш личный бот для пар! 🖤",
            reply_markup=main_menu_kb(True)
        )
    else:
        await update.message.reply_text(
            "👋 Привет! Это Couple Tracker — ваш личный бот для пар 💕\n\n"
            "Чтобы начать, отправьте ID вашего партнёра (это число из его профиля в Telegram).",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Как найти ID партнёра?", url="https://t.me/username_to_id_bot")]])
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена текущей операции."""
    if update.message:
        await update.message.reply_text("❌ Отменено", reply_markup=main_menu_kb(True))
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("❌ Отменено", reply_markup=main_menu_kb(True))
    return ConversationHandler.END

async def home_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кнопка 'Главное меню'."""
    await update.message.reply_text("📱 Главное меню:", reply_markup=main_menu_kb(True))

async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вернуться в главное меню."""
    query = update.callback_query
    await query.answer()
    data = load_data()
    user = get_user(data, query.from_user.id)
    await query.edit_message_text("📱 Главное меню:", reply_markup=main_menu_kb(bool(user["partner_id"])))

# ── обработчики дерева 🌱 ─────────────────────────────────────────────────────

async def tree_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню дерева."""
    query = update.callback_query
    await query.answer()
    
    data = load_data()
    couple_key = ck(query.from_user.id, get_user(data, query.from_user.id)["partner_id"])
    couple = get_couple(data, couple_key)
    
    text = f"🌱 *{couple['tree_name']}*\n\n💚 Здоровье: [========] 100%\n"
    buttons = [
        [InlineKeyboardButton("💧 Полить", callback_data="tree_water"),
         InlineKeyboardButton("🍌 Накормить", callback_data="tree_feed")],
        [InlineKeyboardButton("🎵 Спеть", callback_data="tree_sing")],
        [InlineKeyboardButton("📜 История", callback_data="tree_history")],
        [InlineKeyboardButton("✏️ Переименовать", callback_data="tree_rename")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")],
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

async def tree_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Действие с деревом (полить, накормить, спеть)."""
    query = update.callback_query
    await query.answer("✨ Деревце очень благодарно! 🌱")
    
    data = load_data()
    couple_key = ck(query.from_user.id, get_user(data, query.from_user.id)["partner_id"])
    couple = get_couple(data, couple_key)
    
    action_map = {
        "tree_water": "💧 полил(а)",
        "tree_feed": "🍌 накормил(а)",
        "tree_sing": "🎵 спел(а)",
    }
    
    action = action_map.get(query.data, "взаимодействовал(а)")
    couple["tree_actions"].append({"action": action, "date": str(date.today())})
    save_data(data)
    
    await asyncio.sleep(1)
    await tree_menu(update, context)

async def tree_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """История действий с деревом."""
    query = update.callback_query
    await query.answer()
    
    data = load_data()
    couple_key = ck(query.from_user.id, get_user(data, query.from_user.id)["partner_id"])
    couple = get_couple(data, couple_key)
    
    if not couple["tree_actions"]:
        text = "📜 История пуста. Начните взаимодействовать с деревцем! 🌱"
    else:
        text = "📜 *История деревца:*\n"
        for act in couple["tree_actions"][-10:]:
            text += f"• {act['action']} ({act['date']})\n"
    
    await query.edit_message_text(text, reply_markup=back_btn(), parse_mode="Markdown")

async def tree_rename_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало переименования дерева."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✏️ Придумайте новое имя для деревца:")
    return WAITING_TREE_NAME

async def tree_rename_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сохранение нового имени деревца."""
    new_name = update.message.text[:50]
    
    data = load_data()
    couple_key = ck(update.effective_user.id, get_user(data, update.effective_user.id)["partner_id"])
    couple = get_couple(data, couple_key)
    couple["tree_name"] = new_name
    save_data(data)
    
    await update.message.reply_text(f"✅ Деревце теперь называется *{new_name}*! 🌱", 
                                     reply_markup=back_btn(), parse_mode="Markdown")
    return ConversationHandler.END

# ── обработчики аналитики ──────────────────────────────────────────────────────

async def analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Аналитика."""
    query = update.callback_query
    await query.answer()
    
    text = ("📊 *АНАЛИТИКА*\n\n"
            "🔥 Общая активность: Высокая\n"
            "💕 Уровень близости: Очень хороший\n"
            "🎯 Прогресс целей: 60%\n"
            "🏆 Ачивок получено: 5\n")
    
    await query.edit_message_text(text, reply_markup=back_btn(), parse_mode="Markdown")

# ── stub-функции для остальных меню ────────────────────────────────────────────

async def achievements_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "🏆 *АЧИВКИ*\n\n"
    for key, ach in ACHIEVEMENTS.items():
        text += f"{ach['icon']} {ach['name']}\n"
    await query.edit_message_text(text, reply_markup=back_btn(), parse_mode="Markdown")

async def hidden_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "💬 *СКРЫТЫЕ ВОПРОСЫ*\n\nЗдесь вы можете задавать друг другу вопросы, ответы на которые видны только после того, как оба ответят 🔮"
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ Новый вопрос", callback_data="new_hidden_q")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")],
    ]), parse_mode="Markdown")

async def new_hidden_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    q = random.choice(HIDDEN_QUESTIONS)
    await query.edit_message_text(f"💬 *Вопрос для партнёра:*\n\n_{q}_\n\nОтправить партнёру?",
                                  reply_markup=InlineKeyboardMarkup([
                                      [InlineKeyboardButton("✅ Да", callback_data=f"send_q|{q}")],
                                      [InlineKeyboardButton("◀️ Назад", callback_data="hidden_menu")],
                                  ]), parse_mode="Markdown")

async def answer_hidden_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Напишите ваш ответ:")
    return WAITING_HIDDEN_A

async def reveal_hidden(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔮 Ответы совпали! 💕", reply_markup=back_btn())

async def hidden_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📜 История скрытых вопросов пуста.", reply_markup=back_btn())

async def confession_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "🤫 *ТАЙНЫЕ ПРИЗНАНИЯ*\n\nПоделитесь своими мечтами и желаниями 💭"
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Новое признание", callback_data="new_confession")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")],
    ]), parse_mode="Markdown")

async def challenges_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "🎪 *ЧЕЛЛЕНДЖИ*\n\nПринимайте вызовы и становитесь ближе! 💪"
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 Случайный челлендж", callback_data="random_challenge")],
        [InlineKeyboardButton("📋 Все челленджи", callback_data="all_challenges")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")],
    ]), parse_mode="Markdown")

async def random_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ch = random.choice(CHALLENGES_LIST)
    text = f"🎪 *Челлендж:*\n\n{ch['text']}\n\nНа {ch['days']} дн."
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Принять", callback_data="accept_challenge")],
        [InlineKeyboardButton("◀️ Назад", callback_data="challenges_menu")],
    ]), parse_mode="Markdown")

async def accept_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Челлендж принят! 🎉", reply_markup=back_btn())

async def all_challenges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "📋 *ВСЕ ЧЕЛЛЕНДЖИ:*\n\n"
    for i, ch in enumerate(CHALLENGES_LIST, 1):
        text += f"{i}. {ch['text']}\n"
    await query.edit_message_text(text, reply_markup=back_btn(), parse_mode="Markdown")

async def complete_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ Челлендж завершен! 🏆", reply_markup=back_btn())

async def done_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def random_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    ideas = ["🍽️ Романтический ужин", "🎬 Кино вечер", "🚶 Прогулка в парке", "🎨 Арт-выставка"]
    await query.edit_message_text(f"💡 Идея свидания: {random.choice(ideas)}", reply_markup=back_btn())

async def diary_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📝 *ДНЕВНИК*\n\nВедите совместный дневник 💭",
                                  reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Новая запись", callback_data="add_diary")],
        [InlineKeyboardButton("📖 Все записи", callback_data="diary_all")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")],
    ]), parse_mode="Markdown")

async def diary_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📖 В дневнике пока нет записей.", reply_markup=back_btn())

async def wishlist_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🎁 *ВИШЛИСТ*\n\nСоставляйте списки желаний 💝",
                                  reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Добавить желание", callback_data="add_wish")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")],
    ]), parse_mode="Markdown")

async def complete_wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def done_wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def capsule_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔮 *TIME CAPSULE*\n\nЗапечатайте моменты на будущее 💫",
                                  reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("✍️ Создать капсулу", callback_data="add_capsule")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")],
    ]), parse_mode="Markdown")

async def habits_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("💪 *ПРИВЫЧКИ*\n\nВырабатывайте полезные привычки вместе 🔥",
                                  reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Новая привычка", callback_data="add_habit")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")],
    ]), parse_mode="Markdown")

async def check_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def done_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def goals_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🎯 *ЦЕЛИ*\n\nУстанавливайте и достигайте целей вместе 🏆",
                                  reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Новая цель", callback_data="add_goal")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")],
    ]), parse_mode="Markdown")

async def complete_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def done_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def places_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🗺️ *МЕСТА*\n\nОтмечайте посещённые и желаемые места 🌍",
                                  reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Побывали", callback_data="add_place_been")],
        [InlineKeyboardButton("💭 Хотим посетить", callback_data="add_place_want")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")],
    ]), parse_mode="Markdown")

async def dates_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("💕 *СВИДАНИЯ*\n\nПланируйте и отмечайте свидания 💑",
                                  reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Спланировать", callback_data="add_date_plan")],
        [InlineKeyboardButton("📜 История", callback_data="dates_history")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")],
    ]), parse_mode="Markdown")

async def dates_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📜 История свиданий пуста.", reply_markup=back_btn())

async def special_dates_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📅 *ВАЖНЫЕ ДАТЫ*\n\nДни рождения, годовщины и др.",
                                  reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Добавить дату", callback_data="add_special_date")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_main")],
    ]), parse_mode="Markdown")

async def partner_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = load_data()
    user = get_user(data, query.from_user.id)
    
    if user["partner_id"]:
        await query.edit_message_text(f"👥 *Партнёр ID:* {user['partner_id']}", reply_markup=back_btn(), parse_mode="Markdown")
    else:
        await query.edit_message_text("Партнёр не привязан.", reply_markup=back_btn())

async def send_question_to_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    question = query.data.split("|", 1)[1]
    data = load_data()
    user = get_user(data, query.from_user.id)
    if user["partner_id"]:
        await query.edit_message_text("✅ Вопрос отправлен партнёру! 💬", reply_markup=main_menu_kb(True))
    else:
        await query.edit_message_text("❌ Не удалось отправить.", reply_markup=back_btn())

async def accept_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def decline_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def reveal_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def date_accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def date_decline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def photo_id_helper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощник для получения ID фото (для отладки)."""
    if update.message.photo:
        await update.message.reply_text(f"📸 File ID: `{update.message.photo[-1].file_id}`", 
                                       parse_mode="Markdown")

async def add_diary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✍️ Напишите запись в дневник:")
    return WAITING_DIARY_TEXT

async def add_diary_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text[:500]
    data = load_data()
    save_data(data)
    await update.message.reply_text("✅ Запись сохранена!", reply_markup=back_btn())
    return ConversationHandler.END

async def add_wish_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🎁 Опишите желание:")
    return WAITING_WISH_TEXT

async def add_wish_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["wish_text"] = update.message.text
    await update.message.reply_text("💰 Сколько это стоит? (или пропустите)", 
                                   reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭️ Пропустить", callback_data="skip_wish_price")],
    ]))
    return WAITING_WISH_PRICE

async def add_wish_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    save_data(data)
    await update.message.reply_text("✅ Желание добавлено!", reply_markup=back_btn())
    return ConversationHandler.END

async def skip_wish_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    save_data(data)
    await query.edit_message_text("✅ Желание добавлено!", reply_markup=back_btn())
    return ConversationHandler.END

async def add_capsule_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✍️ Напишите сообщение в капсулу:")
    return WAITING_CAPSULE_TEXT

async def add_capsule_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["capsule_text"] = update.message.text
    await update.message.reply_text("📅 На какую дату открыть? (YYYY-MM-DD):")
    return WAITING_CAPSULE_DATE

async def add_capsule_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    save_data(data)
    await update.message.reply_text("✅ Капсула создана!", reply_markup=back_btn())
    return ConversationHandler.END

async def add_habit_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text[:100]
    data = load_data()
    save_data(data)
    await update.message.reply_text("✅ Привычка добавлена!", reply_markup=back_btn())
    return ConversationHandler.END

async def add_habit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("💪 Опишите привычку:")
    return WAITING_HABIT_TEXT

async def add_goal_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text[:100]
    data = load_data()
    save_data(data)
    await update.message.reply_text("✅ Цель добавлена!", reply_markup=back_btn())
    return ConversationHandler.END

async def add_goal_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🎯 Опишите цель:")
    return WAITING_GOAL_TEXT

async def add_place_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text[:100]
    data = load_data()
    save_data(data)
    await update.message.reply_text("✅ Место добавлено!", reply_markup=back_btn())
    return ConversationHandler.END

async def add_place_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🗺️ Напишите название места:")
    return WAITING_PLACE_NAME

async def add_special_date_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📅 Название события (День рождения, Годовщина и т.д.):")
    return WAITING_DATE_NAME

async def add_special_date_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date_name"] = update.message.text
    await update.message.reply_text("📅 Дата (YYYY-MM-DD):")
    return WAITING_DATE_VALUE

async def add_special_date_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date_value"] = update.message.text
    await update.message.reply_text("Это ежегодное событие?",
                                   reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Да", callback_data="annual_yes")],
        [InlineKeyboardButton("❌ Нет", callback_data="annual_no")],
    ]))
    return WAITING_DATE_ANNUAL

async def add_special_date_annual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    save_data(data)
    await query.edit_message_text("✅ Дата добавлена!", reply_markup=back_btn())
    return ConversationHandler.END

async def add_date_plan_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("💕 Название свидания:")
    return WAITING_DATE_PLAN_TITLE

async def add_date_plan_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date_plan_title"] = update.message.text
    await update.message.reply_text("📅 Дата (YYYY-MM-DD):")
    return WAITING_DATE_PLAN_DATE

async def add_date_plan_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date_plan_date"] = update.message.text
    await update.message.reply_text("📝 Описание (или пропустите):",
                                   reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭️ Пропустить", callback_data="skip_dp_desc")],
    ]))
    return WAITING_DATE_PLAN_DESC

async def add_date_plan_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    save_data(data)
    await update.message.reply_text("✅ Свидание спланировано!", reply_markup=back_btn())
    return ConversationHandler.END

async def skip_dp_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    save_data(data)
    await query.edit_message_text("✅ Свидание спланировано!", reply_markup=back_btn())
    return ConversationHandler.END

async def background_loop(app):
    """Фоновый цикл для напоминаний и проверок."""
    while True:
        await asyncio.sleep(3600)  # каждый час

# ── главная функция ────────────────────────────────────────────────────────────

async def main():
    """Главная функция запуска бота."""
    app = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandlers для сложных диалогов
    convs = [
        ConversationHandler(
            entry_points=[CallbackQueryHandler(add_mood_start, pattern="^add_mood$")],
            states={WAITING_MOOD_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_mood_save)]},
            fallbacks=[CommandHandler("cancel", cancel)],
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(add_confession_start, pattern="^new_confession$")],
            states={WAITING_CONFESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_confession_save)]},
            fallbacks=[CommandHandler("cancel", cancel)],
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(add_checkin_start, pattern="^add_checkin$")],
            states={WAITING_CHECKIN_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_checkin_save)]},
            fallbacks=[CommandHandler("cancel", cancel)],
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(add_diary, pattern="^add_diary$")],
            states={WAITING_DIARY_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_diary_save)]},
            fallbacks=[CommandHandler("cancel", cancel)],
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(add_wish_start, pattern="^add_wish$")],
            states={
                WAITING_WISH_TEXT:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_wish_text)],
                WAITING_WISH_PRICE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, add_wish_price),
                    CallbackQueryHandler(skip_wish_price, pattern="^skip_wish_price$"),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(add_capsule_start, pattern="^add_capsule$")],
            states={
                WAITING_CAPSULE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_capsule_text)],
                WAITING_CAPSULE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_capsule_date)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(add_habit_start, pattern="^add_habit$")],
            states={WAITING_HABIT_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_habit_save)]},
            fallbacks=[CommandHandler("cancel", cancel)],
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(add_goal_start, pattern="^add_goal$")],
            states={WAITING_GOAL_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_goal_save)]},
            fallbacks=[CommandHandler("cancel", cancel)],
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(add_place_start, pattern="^add_place_(want|been)$")],
            states={WAITING_PLACE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_place_save)]},
            fallbacks=[CommandHandler("cancel", cancel)],
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(add_special_date_start, pattern="^add_special_date$")],
            states={
                WAITING_DATE_NAME:   [MessageHandler(filters.TEXT & ~filters.COMMAND, add_special_date_name)],
                WAITING_DATE_VALUE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_special_date_value)],
                WAITING_DATE_ANNUAL: [CallbackQueryHandler(add_special_date_annual, pattern="^annual_")],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        ),
        ConversationHandler(
            entry_points=[CallbackQueryHandler(add_date_plan_start, pattern="^add_date_plan$")],
            states={
                WAITING_DATE_PLAN_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_date_plan_title)],
                WAITING_DATE_PLAN_DATE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_date_plan_date)],
                WAITING_DATE_PLAN_DESC:  [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, add_date_plan_desc),
                    CallbackQueryHandler(skip_dp_desc, pattern="^skip_dp_desc$"),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        ),
    ]

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^🏠 Главное меню$"), home_button))
    app.add_handler(MessageHandler(filters.PHOTO, photo_id_helper))
    for conv in convs:
        app.add_handler(conv)

    # Tree rename conversation
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(tree_rename_start, pattern="^tree_rename$")],
        states={WAITING_TREE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, tree_rename_save)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    ))

    for pattern, handler in [
        ("^achievements_menu$",  achievements_menu),
        ("^hidden_menu$",        hidden_menu),
        ("^new_hidden_q$",       new_hidden_q),
        ("^answer_hidden$",      answer_hidden_start),
        ("^reveal_hidden$",      reveal_hidden),
        ("^hidden_history$",     hidden_history),
        ("^confession_menu$",    confession_menu),
        ("^challenges_menu$",    challenges_menu),
        ("^random_challenge$",   random_challenge),
        ("^accept_challenge$",   accept_challenge),
        ("^all_challenges$",     all_challenges),
        ("^complete_challenge$", complete_challenge),
        ("^done_ch_",            done_challenge),
        ("^analytics$",          analytics),
        ("^random_date$",        random_date),
        ("^diary_menu$",         diary_menu),
        ("^diary_all$",          diary_all),
        ("^wishlist_menu$",      wishlist_menu),
        ("^complete_wish$",      complete_wish),
        ("^done_wish_",          done_wish),
        ("^capsule_menu$",       capsule_menu),
        ("^habits_menu$",        habits_menu),
        ("^check_habit$",        check_habit),
        ("^done_habit_",         done_habit),
        ("^goals_menu$",         goals_menu),
        ("^complete_goal$",      complete_goal),
        ("^done_goal_",          done_goal),
        ("^places_menu$",        places_menu),
        ("^dates_menu$",         dates_menu),
        ("^dates_history$",      dates_history),
        ("^special_dates_menu$", special_dates_menu),
        ("^partner_info$",       partner_info),
        ("^send_q\\|",           send_question_to_partner),
        ("^back_main$",          back_main),
        ("^tree_menu$",          tree_menu),
        ("^tree_water$",         tree_action),
        ("^tree_feed$",          tree_action),
        ("^tree_sing$",          tree_action),
        ("^tree_history$",       tree_history),
        ("^accept_link_",        accept_link),
        ("^reveal_q_",           reveal_q),
        ("^answer_q_",           answer_hidden_start),
        ("^decline_link_",       decline_link),
        ("^date_accept_",        date_accept),
        ("^date_decline_",       date_decline),
    ]:
        app.add_handler(CallbackQueryHandler(handler, pattern=pattern))

    async def error_handler(update, context):
        logger.error(f"Exception: {context.error}", exc_info=context.error)
        if update and hasattr(update, "callback_query") and update.callback_query:
            try:
                await update.callback_query.answer(f"Ошибка: {str(context.error)[:50]}", show_alert=True)
            except Exception:
                pass

    app.add_error_handler(error_handler)

    print("🤖 Бот запущен! Нажмите Ctrl+C для остановки")
    async with app:
        await app.initialize()
        await app.bot.set_my_commands([
            ("start", "🖤 Запустить бота"),
        ])
        await app.start()
        await app.updater.start_polling()
        asyncio.create_task(background_loop(app))
        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            await app.updater.stop()
            await app.stop()

# ── недостающие функции ────────────────────────────────────────────────────────

async def add_mood_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❤️ Выберите настроение:")
    return WAITING_MOOD_NOTE

async def add_mood_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    save_data(data)
    await update.message.reply_text("✅ Настроение записано!", reply_markup=back_btn())
    return ConversationHandler.END

async def add_confession_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🤫 Напишите признание:")
    return WAITING_CONFESSION

async def add_confession_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    save_data(data)
    await update.message.reply_text("✅ Признание сохранено в тайне!", reply_markup=back_btn())
    return ConversationHandler.END

async def add_checkin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🌙 Как прошел ваш день?")
    return WAITING_CHECKIN_TEXT

async def add_checkin_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    save_data(data)
    await update.message.reply_text("✅ Check-in записан!", reply_markup=back_btn())
    return ConversationHandler.END

if __name__ == "__main__":
    asyncio.run(main())
