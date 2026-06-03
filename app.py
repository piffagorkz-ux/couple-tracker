#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import json
import os
from datetime import date, datetime, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "lovio")

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "couple_data.json")
os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users": {}, "couples": {}}

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False

def get_user(data, uid):
    uid = str(uid)
    if "users" not in data:
        data["users"] = {}
    if uid not in data["users"]:
        data["users"][uid] = {
            "name": "", "partner_id": None, "gender": "female",
            "xp": 0, "shop_items": {}, "last_login": ""
        }
    return data["users"][uid]

def ck(id1, id2):
    return f"{min(int(id1), int(id2))}_{max(int(id1), int(id2))}"

def get_couple(data, key):
    if "couples" not in data:
        data["couples"] = {}
    if key not in data["couples"]:
        data["couples"][key] = {
            "diary": [], "mood": [], "goals": [], "places": [],
            "dates_plan": [], "habits": [], "wishes": [], "confessions": [],
            "important_dates": [], "activities": [], "notifications": [],
            "relationship_level": 1, "xp": 0, "created_date": str(date.today()),
            "stats": {"diary": 0, "goals": 0, "places": 0, "closeness": 50}
        }
    if "notifications" not in data["couples"][key]:
        data["couples"][key]["notifications"] = []
    if "relationship_level" not in data["couples"][key]:
        data["couples"][key]["relationship_level"] = 1
    if "xp" not in data["couples"][key]:
        data["couples"][key]["xp"] = 0
    return data["couples"][key]

def add_xp(couple, amount):
    couple["xp"] = couple.get("xp", 0) + amount
    
    xp_thresholds = [0, 100, 300, 600, 1000, 1500]
    level = 1
    for i, threshold in enumerate(xp_thresholds):
        if couple["xp"] >= threshold:
            level = i + 1
    
    old_level = couple.get("relationship_level", 1)
    couple["relationship_level"] = level
    
    return old_level != level

def add_notification(couple, notif_type, text, to_user=None):
    if "notifications" not in couple:
        couple["notifications"] = []
    couple["notifications"].append({
        "type": notif_type,
        "text": text,
        "read": False,
        "to_user": to_user,
        "id": len(couple["notifications"])
    })

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uid = request.form.get("user_id", "").strip()
        name = request.form.get("name", "").strip()
        gender = request.form.get("gender", "female")
        
        if uid and name:
            session["user_id"] = uid
            session["name"] = name
            session["gender"] = gender
            
            data = load_data()
            user = get_user(data, uid)
            user["name"] = name
            user["gender"] = gender
            save_data(data)
            return redirect(url_for("dashboard"))
        
        return render_template("login.html", error="Заполните все поля")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    data = load_data()
    user = get_user(data, session["user_id"])
    
    stats = {
        "name": session.get("name"),
        "gender": session.get("gender"),
        "partner_id": user.get("partner_id"),
        "xp": user.get("xp", 0)
    }
    
    notifications_count = {}
    
    if user.get("partner_id"):
        couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
        stats["stats"] = couple.get("stats", {})
        stats["couple_xp"] = couple.get("xp", 0)
        stats["relationship_level"] = couple.get("relationship_level", 1)
        
        created = couple.get("created_date", str(date.today()))
        days_together = (date.today() - datetime.strptime(created, "%Y-%m-%d").date()).days
        stats["days_together"] = days_together
        
        last_activity = None
        all_activities = couple.get("activities", [])
        if all_activities:
            last_activity = all_activities[-1].get("from")
        stats["last_activity"] = last_activity
        
        if "notifications" in couple:
            for notif in couple["notifications"]:
                if not notif.get("read"):
                    to_user = notif.get("to_user")
                    if to_user is None or str(to_user) == str(session["user_id"]):
                        notif_type = notif.get("type")
                        notifications_count[notif_type] = notifications_count.get(notif_type, 0) + 1
        
        last_login = user.get("last_login", "")
        today = str(date.today())
        if last_login != today:
            add_xp(couple, 1)
            user["last_login"] = today
    
    save_data(data)
    
    return render_template("dashboard.html", stats=stats, notifications=notifications_count)

@app.route("/api/notifications/mark-read", methods=["POST"])
@login_required
def mark_notifications_read():
    data = load_data()
    user = get_user(data, session["user_id"])
    
    if user.get("partner_id"):
        couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
        notif_type = request.json.get("type")
        
        if "notifications" in couple:
            for notif in couple["notifications"]:
                if notif.get("type") == notif_type and not notif.get("read"):
                    to_user = notif.get("to_user")
                    if to_user is None or str(to_user) == str(session["user_id"]):
                        notif["read"] = True
        
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": ""}), 400

@app.route("/diary")
@login_required
def diary():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return redirect(url_for("settings"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("diary.html", entries=couple["diary"])

@app.route("/api/diary/add", methods=["POST"])
@login_required
def diary_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    text = request.json.get("text", "").strip()
    
    if text:
        couple["diary"].append({
            "text": text,
            "author": session.get("name"),
            "date": str(date.today())
        })
        couple["stats"]["diary"] = len(couple["diary"])
        add_xp(couple, 5)
        add_notification(couple, "diary", f"📝 {session.get('name')}: новая запись", to_user=user["partner_id"])
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": ""}), 400

@app.route("/mood")
@login_required
def mood():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return redirect(url_for("settings"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("mood.html", moods=couple["mood"])

@app.route("/api/mood/add", methods=["POST"])
@login_required
def mood_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    mood_level = request.json.get("mood", 5)
    
    couple["mood"].append({
        "level": mood_level,
        "date": str(date.today()),
        "author": session.get("name")
    })
    add_xp(couple, 3)
    add_notification(couple, "mood", f"😊 {session.get('name')}: оценил(а) настроение", to_user=user["partner_id"])
    save_data(data)
    return jsonify({"success": True})

@app.route("/goals")
@login_required
def goals():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return redirect(url_for("settings"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("goals.html", goals=couple["goals"])

@app.route("/api/goals/add", methods=["POST"])
@login_required
def goals_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    text = request.json.get("text", "").strip()
    
    if text:
        couple["goals"].append({
            "id": len(couple["goals"]) + 1,
            "text": text,
            "completed": False,
            "date": str(date.today())
        })
        add_xp(couple, 2)
        add_notification(couple, "goals", f"🎯 {session.get('name')}: новая цель", to_user=user["partner_id"])
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": ""}), 400

@app.route("/api/goals/complete/<int:gid>", methods=["POST"])
@login_required
def goals_complete(gid):
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    
    for goal in couple["goals"]:
        if goal["id"] == gid:
            goal["completed"] = True
            couple["stats"]["goals"] = len([g for g in couple["goals"] if g["completed"]])
            couple["stats"]["closeness"] = min(100, couple["stats"].get("closeness", 50) + 5)
            add_xp(couple, 25)
            save_data(data)
            return jsonify({"success": True})
    
    return jsonify({"error": ""}), 404

@app.route("/places")
@login_required
def places():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return redirect(url_for("settings"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("places.html", places=couple["places"])

@app.route("/api/places/add", methods=["POST"])
@login_required
def places_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    name = request.json.get("name", "").strip()
    
    if name:
        couple["places"].append({
            "name": name,
            "visited": False,
            "date": str(date.today())
        })
        couple["stats"]["places"] = len([p for p in couple["places"] if p.get("visited")])
        add_xp(couple, 2)
        add_notification(couple, "places", f"🗺️ {session.get('name')}: новое место", to_user=user["partner_id"])
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": ""}), 400

@app.route("/api/places/visit", methods=["POST"])
@login_required
def places_visit():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    name = request.json.get("name", "").strip()
    
    for place in couple["places"]:
        if place.get("name") == name:
            place["visited"] = True
            couple["stats"]["places"] = len([p for p in couple["places"] if p.get("visited")])
            add_xp(couple, 10)
            save_data(data)
            return jsonify({"success": True})
    
    return jsonify({"error": ""}), 404

@app.route("/dates")
@login_required
def dates():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return redirect(url_for("settings"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("dates.html", dates=couple["dates_plan"], current_user=session["user_id"])

@app.route("/api/dates/add", methods=["POST"])
@login_required
def dates_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    title = request.json.get("title", "").strip()
    date_val = request.json.get("date", "")
    time_val = request.json.get("time", "")
    
    if title and date_val:
        couple["dates_plan"].append({
            "id": len(couple["dates_plan"]),
            "title": title,
            "date": date_val,
            "time": time_val,
            "status": "pending",
            "created_by": str(session["user_id"])
        })
        add_xp(couple, 5)
        add_notification(couple, "dates", f"💋 {session.get('name')}: предложил(а) свидание - {title}", to_user=user["partner_id"])
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": ""}), 400

@app.route("/api/dates/respond/<int:did>", methods=["POST"])
@login_required
def dates_respond(did):
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    response = request.json.get("response")
    
    if did < len(couple["dates_plan"]):
        date_event = couple["dates_plan"][did]
        
        if response == "accept":
            date_event["status"] = "accepted"
            add_xp(couple, 20)
            add_notification(couple, "dates", f"✅ {session.get('name')}: согласился на свидание - {date_event['title']}", to_user=date_event["created_by"])
        else:
            date_event["status"] = "declined"
            add_notification(couple, "dates", f"❌ {session.get('name')}: отказался от свидания - {date_event['title']}", to_user=date_event["created_by"])
        
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": ""}), 404

@app.route("/api/dates/complete/<int:did>", methods=["POST"])
@login_required
def dates_complete(did):
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    
    if did < len(couple["dates_plan"]):
        date_event = couple["dates_plan"][did]
        if date_event["status"] == "accepted":
            date_event["status"] = "completed"
            add_xp(couple, 50)
            save_data(data)
            return jsonify({"success": True})
    
    return jsonify({"error": ""}), 404

@app.route("/habits")
@login_required
def habits():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return redirect(url_for("settings"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("habits.html", habits=couple["habits"])

@app.route("/api/habits/add", methods=["POST"])
@login_required
def habits_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    text = request.json.get("text", "").strip()
    
    if text:
        couple["habits"].append({
            "text": text,
            "created": str(date.today()),
            "streak": 0,
            "completed_dates": []
        })
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": ""}), 400

@app.route("/api/habits/complete/<int:hid>", methods=["POST"])
@login_required
def habits_complete(hid):
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    
    if hid < len(couple["habits"]):
        habit = couple["habits"][hid]
        today = str(date.today())
        if today not in habit.get("completed_dates", []):
            habit["completed_dates"].append(today)
            habit["streak"] = len(habit["completed_dates"])
            add_xp(couple, 10)
            save_data(data)
            return jsonify({"success": True})
    
    return jsonify({"error": ""}), 404

@app.route("/wishes")
@login_required
def wishes():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return redirect(url_for("settings"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("wishes.html", wishes=couple["wishes"])

@app.route("/api/wishes/add", methods=["POST"])
@login_required
def wishes_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    text = request.json.get("text", "").strip()
    price = request.json.get("price", 0)
    
    if text:
        couple["wishes"].append({
            "text": text,
            "price": price,
            "gifted": False,
            "date": str(date.today())
        })
        add_xp(couple, 2)
        add_notification(couple, "wishes", f"🎁 {session.get('name')}: новое желание", to_user=user["partner_id"])
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": ""}), 400

@app.route("/api/wishes/gift", methods=["POST"])
@login_required
def wishes_gift():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    text = request.json.get("text", "").strip()
    
    for wish in couple["wishes"]:
        if wish.get("text") == text:
            wish["gifted"] = True
            add_xp(couple, 30)
            save_data(data)
            return jsonify({"success": True})
    
    return jsonify({"error": ""}), 404

@app.route("/confessions")
@login_required
def confessions():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return redirect(url_for("settings"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("confessions.html", confessions=couple["confessions"])

@app.route("/api/confessions/add", methods=["POST"])
@login_required
def confessions_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    text = request.json.get("text", "").strip()
    
    if text:
        couple["confessions"].append({
            "text": text,
            "date": str(date.today()),
            "author": session.get("name")
        })
        add_xp(couple, 15)
        add_notification(couple, "confessions", f"💌 {session.get('name')}: новое признание", to_user=user["partner_id"])
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": ""}), 400

@app.route("/important-dates")
@login_required
def important_dates():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return redirect(url_for("settings"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("important_dates.html", dates=couple["important_dates"])

@app.route("/api/important-dates/add", methods=["POST"])
@login_required
def important_dates_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    title = request.json.get("title", "").strip()
    date_val = request.json.get("date", "")
    
    if title and date_val:
        couple["important_dates"].append({
            "title": title,
            "date": date_val
        })
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": ""}), 400

@app.route("/activities")
@login_required
def activities():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return redirect(url_for("settings"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    
    gender = session.get("gender")
    
    if gender == "male":
        tasks = [
            "💪 Поддержка партнёру",
            "🤗 Длинные объятия",
            "❤️ Близость",
            "💬 Глубокий разговор",
            "🎁 Неожиданный подарок",
            "👂 Внимательно слушать",
            "🍽️ Приготовить ужин",
            "🧼 Помощь по дому",
            "🎬 Вечер вместе",
            "📞 Позвонить просто так"
        ]
    else:
        tasks = [
            "💋 Комплимент",
            "💋 Романтическое свидание",
            "🌹 Цветы",
            "💌 Любовное письмо",
            "🎀 Сюрприз",
            "🎬 Фильм вместе",
            "🍽️ Готовка вместе",
            "💄 Красивая укладка",
            "💃 Танец вместе",
            "🎵 Любимую песню"
        ]
    
    today_activity = None
    for activity in couple.get("activities", []):
        if activity.get("date") == str(date.today()):
            today_activity = activity
            break
    
    return render_template("activities.html", activities=couple["activities"], tasks=tasks, today_activity=today_activity, gender=gender)

@app.route("/api/activities/select", methods=["POST"])
@login_required
def activities_select():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    task = request.json.get("task", "").strip()
    
    if task:
        couple["activities"].append({
            "task": task,
            "from": session.get("name"),
            "date": str(date.today()),
            "completed": False
        })
        add_xp(couple, 8)
        add_notification(couple, "activities", f"📋 {session.get('name')}: выбрал(а) активность", to_user=user["partner_id"])
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": ""}), 400

@app.route("/api/random-date")
@login_required
def random_date_api():
    import random
    ideas = [
        {"emoji": "🍽️", "text": "Романтический ужин дома"},
        {"emoji": "🎬", "text": "Кино вечер с попкорном"},
        {"emoji": "🚶", "text": "Прогулка в парке"},
        {"emoji": "🎨", "text": "Посещение выставки"},
        {"emoji": "🎪", "text": "Концерт"},
        {"emoji": "🏖️", "text": "Пикник на природе"},
    ]
    return jsonify(random.choice(ideas))

@app.route("/shop")
@login_required
def shop():
    data = load_data()
    user = get_user(data, session["user_id"])
    partner_id = user.get("partner_id")
    if not partner_id:
        return redirect(url_for("settings"))
    
    couple = get_couple(data, ck(session["user_id"], partner_id))
    couple_xp = couple.get("xp", 0)
    
    shop_items = {
        "theme_dark": {"name": "Тёмная тема", "cost": 100, "icon": "🌙"},
        "theme_light": {"name": "Светлая тема", "cost": 100, "icon": "☀️"},
        "pet_cat": {"name": "Кот", "cost": 200, "icon": "🐱"},
        "pet_dog": {"name": "Собака", "cost": 200, "icon": "🐶"},
        "pet_bunny": {"name": "Кролик", "cost": 150, "icon": "🐰"},
        "frame_gold": {"name": "Золотая рамка", "cost": 250, "icon": "🏆"},
        "frame_silver": {"name": "Серебряная рамка", "cost": 150, "icon": "💎"},
        "anim_hearts": {"name": "Анимация сердец", "cost": 300, "icon": "💖"},
        "anim_sparkle": {"name": "Анимация блеска", "cost": 300, "icon": "✨"},
    }
    
    user_items = user.get("shop_items", {})
    
    return render_template("shop.html", shop_items=shop_items, couple_xp=couple_xp, user_items=user_items)

@app.route("/api/shop/buy/<item_id>", methods=["POST"])
@login_required
def shop_buy(item_id):
    data = load_data()
    user = get_user(data, session["user_id"])
    
    if not user.get("partner_id"):
        return jsonify({"error": ""}), 400
    
    shop_items = {
        "theme_dark": 100, "theme_light": 100, "pet_cat": 200,
        "pet_dog": 200, "pet_bunny": 150, "frame_gold": 250,
        "frame_silver": 150, "anim_hearts": 300, "anim_sparkle": 300,
    }
    
    if item_id not in shop_items:
        return jsonify({"error": ""}), 400
    
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    cost = shop_items[item_id]
    couple_xp = couple.get("xp", 0)
    
    if couple_xp >= cost:
        couple["xp"] -= cost
        if "shop_items" not in user:
            user["shop_items"] = {}
        user["shop_items"][item_id] = True
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": "Not enough XP"}), 400

@app.route("/settings")
@login_required
def settings():
    data = load_data()
    user = get_user(data, session["user_id"])
    return render_template("settings.html", 
        name=session.get("name"), 
        user_id=session["user_id"], 
        partner_id=user.get("partner_id"), 
        gender=session.get("gender"))

@app.route("/api/settings/update", methods=["POST"])
@login_required
def settings_update():
    name = request.json.get("name", "").strip()
    
    if name:
        session["name"] = name
        data = load_data()
        get_user(data, session["user_id"])["name"] = name
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": "Invalid"}), 400

@app.route("/api/partner/set", methods=["POST"])
@login_required
def set_partner():
    uid = session["user_id"]
    pid = request.json.get("partner_id", "").strip()
    
    if not pid or pid == uid:
        return jsonify({"error": "Invalid"}), 400
    
    data = load_data()
    get_user(data, uid)["partner_id"] = pid
    get_user(data, pid)["partner_id"] = uid
    get_couple(data, ck(uid, pid))
    save_data(data)
    return jsonify({"success": True})

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
