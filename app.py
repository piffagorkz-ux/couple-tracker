#!/usr/bin/env python3
"""💕 LOVIO - Приложение для пар"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import json, os, random
from datetime import datetime, date, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "lovio-key")
DATA_DIR = os.getenv("DATA_DIR", "data")
DATA_FILE = os.path.join(DATA_DIR, "couple_data.json")
os.makedirs(DATA_DIR, exist_ok=True)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            return json.load(open(DATA_FILE, "r", encoding="utf-8"))
        except:
            return {"users": {}, "couples": {}}
    return {"users": {}, "couples": {}}

def save_data(data):
    json.dump(data, open(DATA_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def get_user(data, uid):
    uid = str(uid)
    if "users" not in data: data["users"] = {}
    if uid not in data["users"]:
        data["users"][uid] = {"name": "", "partner_id": None}
    return data["users"][uid]

def ck(id1, id2):
    return f"{min(int(id1), int(id2))}_{max(int(id1), int(id2))}"

def get_couple(data, key):
    if "couples" not in data: data["couples"] = {}
    if key not in data["couples"]:
        data["couples"][key] = {
            "tree_name": "💕 Наше деревце", "tree_health": 100, "tree_actions": [],
            "diary": [], "mood": [], "checkins": [], "goals": [], "places": [],
            "dates_plan": [], "important_dates": [], "habits": [], "confessions": [],
            "wishes": [], "challenges": [],
            "stats": {"diary": 0, "goals": 0, "places": 0, "checkins": 0, "closeness": 50}
        }
    return data["couples"][key]

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session: return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uid, name = request.form.get("user_id", "").strip(), request.form.get("name", "").strip()
        if uid and name:
            session["user_id"], session["name"] = uid, name
            data = load_data()
            get_user(data, uid)["name"] = name
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
    stats = {"name": session.get("name"), "partner_id": user.get("partner_id")}
    if user.get("partner_id"):
        couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
        stats["stats"] = couple.get("stats", {})
    return render_template("dashboard.html", stats=stats)

@app.route("/tree")
@login_required
def tree():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return redirect(url_for("partner"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("tree.html", tree_name=couple["tree_name"], health=couple.get("tree_health", 100), actions=couple["tree_actions"][-10:])

@app.route("/api/tree/action", methods=["POST"])
@login_required
def tree_action():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    action = request.json.get("action")
    if action in {"water", "feed", "sing"}:
        couple["tree_actions"].append({"action": {"water":"💧 полил(а)", "feed":"🍌 накормил(а)", "sing":"🎵 спел(а)"}[action], "date": str(date.today())})
        couple["tree_health"] = min(100, couple.get("tree_health", 100) + 5)
        couple["stats"]["closeness"] = min(100, couple["stats"].get("closeness", 50) + 2)
        save_data(data)
        return jsonify({"success": True, "health": couple["tree_health"]})
    return jsonify({"error": ""}), 400

@app.route("/tree/rename", methods=["POST"])
@login_required
def tree_rename():
    data = load_data()
    user = get_user(data, session["user_id"])
    if user["partner_id"]:
        couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
        couple["tree_name"] = request.form.get("new_name", "").strip()[:50]
        save_data(data)
    return redirect(url_for("tree"))

@app.route("/diary")
@login_required
def diary():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return redirect(url_for("partner"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("diary.html", entries=couple["diary"])

@app.route("/api/diary/add", methods=["POST"])
@login_required
def diary_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    couple["diary"].append({"text": request.json.get("text"), "author": session.get("name"), "date": str(date.today())})
    couple["stats"]["diary"] = len(couple["diary"])
    save_data(data)
    return jsonify({"success": True})

@app.route("/mood")
@login_required
def mood():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return redirect(url_for("partner"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("mood.html", moods=couple["mood"])

@app.route("/api/mood/add", methods=["POST"])
@login_required
def mood_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    couple["mood"].append({"level": request.json.get("mood", 5), "note": request.json.get("note", ""), "date": str(date.today()), "author": session.get("name")})
    save_data(data)
    return jsonify({"success": True})

@app.route("/checkin")
@login_required
def checkin():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return redirect(url_for("partner"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("checkin.html", checkins=couple["checkins"])

@app.route("/api/checkin/add", methods=["POST"])
@login_required
def checkin_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    couple["checkins"].append({"text": request.json.get("text"), "date": str(date.today()), "author": session.get("name")})
    couple["stats"]["checkins"] += 1
    save_data(data)
    return jsonify({"success": True})

@app.route("/places")
@login_required
def places():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return redirect(url_for("partner"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("places.html", places=couple["places"])

@app.route("/api/places/add", methods=["POST"])
@login_required
def places_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    couple["places"].append({"name": request.json.get("name"), "type": request.json.get("type", "visited"), "date": str(date.today())})
    couple["stats"]["places"] = len([p for p in couple["places"] if p.get("type") == "visited"])
    save_data(data)
    return jsonify({"success": True})

@app.route("/dates")
@login_required
def dates():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return redirect(url_for("partner"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("dates.html", dates=couple["dates_plan"])

@app.route("/api/dates/add", methods=["POST"])
@login_required
def dates_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    couple["dates_plan"].append({"title": request.json.get("title"), "date": request.json.get("date"), "created": str(date.today())})
    save_data(data)
    return jsonify({"success": True})

@app.route("/goals")
@login_required
def goals():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return redirect(url_for("partner"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("goals.html", goals=couple["goals"])

@app.route("/api/goals/add", methods=["POST"])
@login_required
def goals_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    couple["goals"].append({"id": len(couple["goals"])+1, "text": request.json.get("text"), "completed": False, "date": str(date.today())})
    save_data(data)
    return jsonify({"success": True})

@app.route("/api/goals/complete/<int:gid>", methods=["POST"])
@login_required
def goals_complete(gid):
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    for g in couple["goals"]:
        if g["id"] == gid:
            g["completed"] = True
            couple["stats"]["goals"] = len([x for x in couple["goals"] if x["completed"]])
            couple["stats"]["closeness"] = min(100, couple["stats"].get("closeness", 50) + 5)
            save_data(data)
            return jsonify({"success": True})
    return jsonify({"error": ""}), 404

@app.route("/habits")
@login_required
def habits():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return redirect(url_for("partner"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("habits.html", habits=couple["habits"])

@app.route("/api/habits/add", methods=["POST"])
@login_required
def habits_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    couple["habits"].append({"text": request.json.get("text"), "created": str(date.today()), "streak": 0})
    save_data(data)
    return jsonify({"success": True})

@app.route("/wishes")
@login_required
def wishes():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return redirect(url_for("partner"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("wishes.html", wishes=couple["wishes"])

@app.route("/api/wishes/add", methods=["POST"])
@login_required
def wishes_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    couple["wishes"].append({"text": request.json.get("text"), "price": request.json.get("price", 0), "date": str(date.today())})
    save_data(data)
    return jsonify({"success": True})

@app.route("/confessions")
@login_required
def confessions():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return redirect(url_for("partner"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("confessions.html", confessions=couple["confessions"])

@app.route("/api/confessions/add", methods=["POST"])
@login_required
def confessions_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    couple["confessions"].append({"text": request.json.get("text"), "date": str(date.today()), "author": session.get("name")})
    save_data(data)
    return jsonify({"success": True})

@app.route("/important-dates")
@login_required
def important_dates():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return redirect(url_for("partner"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("important_dates.html", dates=couple["important_dates"])

@app.route("/api/important-dates/add", methods=["POST"])
@login_required
def important_dates_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    couple["important_dates"].append({"title": request.json.get("title"), "date": request.json.get("date")})
    save_data(data)
    return jsonify({"success": True})

@app.route("/challenges")
@login_required
def challenges():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return redirect(url_for("partner"))
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    return render_template("challenges.html", challenges=couple["challenges"])

@app.route("/api/challenges/add", methods=["POST"])
@login_required
def challenges_add():
    data = load_data()
    user = get_user(data, session["user_id"])
    if not user["partner_id"]: return jsonify({"error": ""}), 400
    couple = get_couple(data, ck(session["user_id"], user["partner_id"]))
    couple["challenges"].append({"text": request.json.get("text"), "date": str(date.today()), "completed": False})
    save_data(data)
    return jsonify({"success": True})

@app.route("/api/random-date")
@login_required
def random_date_api():
    ideas = [
        {"emoji": "🍽️", "text": "Романтический ужин дома"},
        {"emoji": "🎬", "text": "Кино вечер с попкорном"},
        {"emoji": "🚶", "text": "Прогулка в парке"},
        {"emoji": "🎨", "text": "Арт-выставка"},
        {"emoji": "🎪", "text": "Концерт"},
    ]
    return jsonify(random.choice(ideas))

@app.route("/partner")
@login_required
def partner():
    data = load_data()
    user = get_user(data, session["user_id"])
    return render_template("partner.html", partner_id=user.get("partner_id"), user_id=session["user_id"])

@app.route("/api/partner/set", methods=["POST"])
@login_required
def set_partner():
    uid, pid = session["user_id"], request.json.get("partner_id", "").strip()
    if not pid or pid == uid: return jsonify({"error": "Invalid"}), 400
    data = load_data()
    get_user(data, uid)["partner_id"] = pid
    get_user(data, pid)["partner_id"] = uid
    get_couple(data, ck(uid, pid))
    save_data(data)
    return jsonify({"success": True})

@app.route("/settings")
@login_required
def settings():
    data = load_data()
    user = get_user(data, session["user_id"])
    return render_template("settings.html", name=session.get("name"), user_id=session["user_id"], partner_id=user.get("partner_id"))

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

@app.errorhandler(404)
def not_found(e): return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e): return render_template("500.html"), 500

@app.route("/health")
def health(): return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
