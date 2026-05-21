#!/usr/bin/env python3
"""
🖤 Couple Tracker Web App — Flask версия
Веб-интерфейс для Telegram бота
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import json
import os
from datetime import datetime, date, timedelta
from functools import wraps
import hashlib

app = Flask(__name__)
CORS(app)

# 🔐 Секретный ключ для сессий
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-secret-key-change-me")

# 📁 Пути к файлам данных
DATA_DIR = os.getenv("DATA_DIR", "data")
DATA_FILE = os.path.join(DATA_DIR, "couple_data.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ── ФУНКЦИИ ДЛЯ РАБОТЫ С ДАННЫМИ ────────────────────────────────────────────

def load_data() -> dict:
    """Загружает данные из JSON."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(data: dict):
    """Сохраняет данные в JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data: dict, user_id) -> dict:
    """Получает или создает пользователя."""
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "partner_id": None,
            "name": "",
            "last_seen": str(date.today()),
            "moods": []
        }
    return data[uid]

def ck(id1, id2) -> str:
    """Генерирует уникальный ключ пары."""
    return f"{min(int(id1), int(id2))}_{max(int(id1), int(id2))}"

def get_couple(data: dict, key: str) -> dict:
    """Получает или создает данные пары."""
    if "couples" not in data:
        data["couples"] = {}
    if key not in data["couples"]:
        data["couples"][key] = {
            "important_dates": [],
            "dates_plan": [],
            "moods": {},
            "goals": [],
            "places": [],
            "checkins": {},
            "diary": [],
            "wishlist": [],
            "capsules": [],
            "habits": [],
            "achievements": [],
            "challenges": [],
            "confessions": [],
            "hidden_q": "",
            "hidden_answers": {},
            "tree_actions": [],
            "tree_name": "🌱 Наше деревце",
            "tree_health": 100
        }
    return data["couples"][key]

def login_required(f):
    """Декоратор для проверки логина."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ── МАРШРУТЫ ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Главная страница."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Страница логина."""
    if request.method == "POST":
        user_id = request.form.get("user_id", "").strip()
        name = request.form.get("name", "").strip()
        
        if user_id and name:
            session["user_id"] = user_id
            session["name"] = name
            
            data = load_data()
            user = get_user(data, user_id)
            user["name"] = name
            user["last_seen"] = str(date.today())
            save_data(data)
            
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Заполните все поля")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Выход из аккаунта."""
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    """Главный дашборд."""
    user_id = session.get("user_id")
    data = load_data()
    user = get_user(data, user_id)
    
    stats = {
        "name": session.get("name", ""),
        "partner_id": user.get("partner_id"),
        "last_seen": user.get("last_seen")
    }
    
    return render_template("dashboard.html", stats=stats)

@app.route("/tree")
@login_required
def tree():
    """Страница деревца."""
    user_id = session.get("user_id")
    data = load_data()
    user = get_user(data, user_id)
    
    if not user["partner_id"]:
        return redirect(url_for("partner"))
    
    couple_key = ck(user_id, user["partner_id"])
    couple = get_couple(data, couple_key)
    
    return render_template("tree.html", 
                         tree_name=couple["tree_name"],
                         tree_health=couple.get("tree_health", 100),
                         actions=couple["tree_actions"][-10:])

@app.route("/api/tree/action", methods=["POST"])
@login_required
def tree_action():
    """API для действий с деревом."""
    user_id = session.get("user_id")
    action = request.json.get("action")
    
    data = load_data()
    user = get_user(data, user_id)
    
    if not user["partner_id"]:
        return jsonify({"error": "Партнёр не привязан"}), 400
    
    couple_key = ck(user_id, user["partner_id"])
    couple = get_couple(data, couple_key)
    
    action_map = {
        "water": "💧 полил(а)",
        "feed": "🍌 накормил(а)",
        "sing": "🎵 спел(а)"
    }
    
    if action in action_map:
        couple["tree_actions"].append({
            "action": action_map[action],
            "date": str(date.today())
        })
        couple["tree_health"] = min(100, couple.get("tree_health", 100) + 5)
        save_data(data)
        
        return jsonify({"success": True, "health": couple["tree_health"]})
    
    return jsonify({"error": "Неизвестное действие"}), 400

@app.route("/tree/rename", methods=["POST"])
@login_required
def tree_rename():
    """Переименование деревца."""
    user_id = session.get("user_id")
    new_name = request.form.get("new_name", "").strip()[:50]
    
    if not new_name:
        return jsonify({"error": "Введите имя"}), 400
    
    data = load_data()
    user = get_user(data, user_id)
    
    if not user["partner_id"]:
        return jsonify({"error": "Партнёр не привязан"}), 400
    
    couple_key = ck(user_id, user["partner_id"])
    couple = get_couple(data, couple_key)
    couple["tree_name"] = new_name
    save_data(data)
    
    return redirect(url_for("tree"))

@app.route("/diary")
@login_required
def diary():
    """Страница дневника."""
    user_id = session.get("user_id")
    data = load_data()
    user = get_user(data, user_id)
    
    if not user["partner_id"]:
        return redirect(url_for("partner"))
    
    couple_key = ck(user_id, user["partner_id"])
    couple = get_couple(data, couple_key)
    
    return render_template("diary.html", entries=couple["diary"])

@app.route("/api/diary/add", methods=["POST"])
@login_required
def diary_add():
    """Добавление записи в дневник."""
    user_id = session.get("user_id")
    text = request.json.get("text", "").strip()
    
    if not text:
        return jsonify({"error": "Пустая запись"}), 400
    
    data = load_data()
    user = get_user(data, user_id)
    
    if not user["partner_id"]:
        return jsonify({"error": "Партнёр не привязан"}), 400
    
    couple_key = ck(user_id, user["partner_id"])
    couple = get_couple(data, couple_key)
    
    couple["diary"].append({
        "text": text,
        "author": session.get("name"),
        "date": str(date.today())
    })
    save_data(data)
    
    return jsonify({"success": True})

@app.route("/partner")
@login_required
def partner():
    """Страница связи с партнёром."""
    user_id = session.get("user_id")
    data = load_data()
    user = get_user(data, user_id)
    
    return render_template("partner.html", 
                         partner_id=user.get("partner_id"),
                         user_id=user_id)

@app.route("/api/partner/set", methods=["POST"])
@login_required
def set_partner():
    """Привязка партнёра по ID."""
    user_id = session.get("user_id")
    partner_id = request.json.get("partner_id", "").strip()
    
    if not partner_id or partner_id == user_id:
        return jsonify({"error": "Некорректный ID партнёра"}), 400
    
    data = load_data()
    user = get_user(data, user_id)
    partner = get_user(data, partner_id)
    
    user["partner_id"] = partner_id
    partner["partner_id"] = user_id
    
    # Создаём пару
    couple_key = ck(user_id, partner_id)
    get_couple(data, couple_key)
    
    save_data(data)
    
    return jsonify({"success": True})

@app.route("/goals")
@login_required
def goals():
    """Страница целей."""
    user_id = session.get("user_id")
    data = load_data()
    user = get_user(data, user_id)
    
    if not user["partner_id"]:
        return redirect(url_for("partner"))
    
    couple_key = ck(user_id, user["partner_id"])
    couple = get_couple(data, couple_key)
    
    return render_template("goals.html", goals=couple["goals"])

@app.route("/api/goals/add", methods=["POST"])
@login_required
def goals_add():
    """Добавление цели."""
    user_id = session.get("user_id")
    text = request.json.get("text", "").strip()
    
    if not text:
        return jsonify({"error": "Пустая цель"}), 400
    
    data = load_data()
    user = get_user(data, user_id)
    
    if not user["partner_id"]:
        return jsonify({"error": "Партнёр не привязан"}), 400
    
    couple_key = ck(user_id, user["partner_id"])
    couple = get_couple(data, couple_key)
    
    couple["goals"].append({
        "id": len(couple["goals"]) + 1,
        "text": text,
        "completed": False,
        "date": str(date.today())
    })
    save_data(data)
    
    return jsonify({"success": True})

@app.route("/api/goals/complete/<int:goal_id>", methods=["POST"])
@login_required
def goals_complete(goal_id):
    """Завершение цели."""
    user_id = session.get("user_id")
    data = load_data()
    user = get_user(data, user_id)
    
    if not user["partner_id"]:
        return jsonify({"error": "Партнёр не привязан"}), 400
    
    couple_key = ck(user_id, user["partner_id"])
    couple = get_couple(data, couple_key)
    
    for goal in couple["goals"]:
        if goal["id"] == goal_id:
            goal["completed"] = True
            save_data(data)
            return jsonify({"success": True})
    
    return jsonify({"error": "Цель не найдена"}), 404

@app.route("/challenges")
@login_required
def challenges():
    """Страница челленджей."""
    return render_template("challenges.html")

@app.route("/settings")
@login_required
def settings():
    """Страница настроек."""
    user_id = session.get("user_id")
    data = load_data()
    user = get_user(data, user_id)
    
    return render_template("settings.html", 
                         name=session.get("name"),
                         user_id=user_id,
                         partner_id=user.get("partner_id"))

@app.route("/api/settings/update", methods=["POST"])
@login_required
def settings_update():
    """Обновление настроек."""
    user_id = session.get("user_id")
    name = request.json.get("name", "").strip()
    
    if name:
        session["name"] = name
        data = load_data()
        user = get_user(data, user_id)
        user["name"] = name
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": "Введите имя"}), 400

# ── ОШИБКИ ──────────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(error):
    """Ошибка 404."""
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(error):
    """Ошибка 500."""
    return render_template("500.html"), 500

# ── ТЕСТОВЫЙ МАРШРУТ ────────────────────────────────────────────────────────

@app.route("/health")
def health():
    """Проверка здоровья приложения."""
    return jsonify({
        "status": "ok",
        "timestamp": str(datetime.now()),
        "data_file": DATA_FILE
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
