#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import json
import os
from datetime import date
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
        data["users"][uid] = {"name": "", "partner_id": None, "gender": "female"}
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
            "stats": {"diary": 0, "goals": 0, "places": 0, "closeness": 50}
        }
    if "notifications" not in data["couples"][key]:
        data["couples"][key]["notifications"] = []
    return data["couples"][key]

def add_notification(couple, notif_type, text):
    if "notifications" not in couple:
        couple["notifications"] = []
    couple["notifications"].append({"type": notif_type, "text": text, "read": False})

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
        "partner_id": user.get("partner_id")
    }
    
    notifications_count = {}
    
    if user.get("partner_id"):
        couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
        stats["stats"] = couple.get("stats", {})
        
        if "notifications" in couple:
            for notif in couple["notifications"]:
                notif_type = notif.get("type")
                if not notif.get("read"):
                    notifications_count[notif_type] = notifications_count.get(notif_type, 0) + 1
    
    return render_template("dashboard.html", stats=stats, notifications=notifications_count)

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
        add_notification(couple, "diary", f"📝 {session.get('name')}: новая запись")
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
    add_notification(couple, "mood", f"😊 {session.get('name')}: оценил(а) настроение")
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
        add_notification(couple, "goals", f"🎯 {session.get('name')}: новая цель")
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
        add_notification(couple, "places", f"🗺️ {session.get('name')}: новое место")
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
    return render_template("dates.html", dates=couple["dates_plan"])

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
            "title": title,
            "date": date_val,
            "time": time_val,
            "status": "pending"
        })
        add_notification(couple, "dates", f"💋 {session.get('name')}: предложил(а) свидание")
        save_data(data)
        return jsonify({"success": True})
    
    return jsonify({"error": ""}), 400

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
        add_notification(couple, "wishes", f"🎁 {session.get('name')}: новое желание")
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
        add_notification(couple, "confessions", f"💌 {session.get('name')}: новое признание")
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
        add_notification(couple, "activities", f"📋 {session.get('name')}: выбрал(а) активность")
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
