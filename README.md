# LOVIO v2.0 - Professional Edition

A premium web application for couples to celebrate their relationship with modern tech stack.

## 🎯 Features

- ✅ **Secure Authentication** - Registration, Login with password hashing
- ✅ **Couple Invitation System** - Send, accept, decline invitations
- ✅ **PostgreSQL Database** - Reliable data storage with SQLAlchemy ORM
- ✅ **XP System** - Protected against exploits, daily limits
- ✅ **5 Relationship Levels** - Newbies → Legendary
- ✅ **Multiple Features** - Diary, Mood, Goals, Dates, Habits, Wishes, Confessions
- ✅ **Streak System** - Track daily activity streaks
- ✅ **PWA Ready** - Install on iOS/Android as app
- ✅ **Montserrat Font & Premium Design** - Beautiful UI/UX
- ✅ **CSRF Protection** - Secure against attacks
- ✅ **Data Validation** - All inputs validated

## 🛠️ Tech Stack

- **Backend**: Python 3.9+, Flask 3.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **PWA**: Service Worker, Web App Manifest
- **Security**: Werkzeug password hashing, CSRF-protection

## 📦 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip

### Local Setup

1. **Clone the repository**
```bash
git clone <repo-url>
cd lovio
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure .env**
```bash
cp .env.example .env
# Edit .env with your PostgreSQL connection string and SECRET_KEY
```

5. **Initialize database**
```bash
flask db upgrade
```

6. **Run the app**
```bash
flask run
```

Visit `http://localhost:5000`

## 🚀 Deployment (Render.com)

1. **Push to GitHub**
```bash
git add .
git commit -m "LOVIO v2.0 Production Ready"
git push
```

2. **Create Render Service**
- Go to render.com
- Create new Web Service
- Connect GitHub repository
- Set environment variables:
  - `FLASK_ENV=production`
  - `SECRET_KEY=<generate-strong-key>`
  - `DATABASE_URL=<your-postgres-url>`

3. **Run migrations on deploy**
- Add this to Render startup command:
```bash
flask db upgrade && gunicorn 'app:create_app()'
```

## 📋 Database Schema

### Users
- username (unique)
- email (unique)
- password_hash (Werkzeug hashed)
- name, gender
- xp, last_login, last_check_in
- couple_id (FK)

### Couples
- user1_id, user2_id
- xp, relationship_level
- closeness (0-100)
- couple_since (date)

### Related Tables
- Goals, Diary, Mood, Places, DatePlan
- Habit, Wish, Confession, Activity
- Notification, CoupleInvitation

## 🔒 Security

✅ **Password Security** - Werkzeug generate_password_hash/check_password_hash
✅ **CSRF Protection** - Flask-WTF CSRF tokens
✅ **Data Validation** - All inputs validated (length, type, range)
✅ **SQL Injection** - SQLAlchemy parameterized queries
✅ **XP Limits** - Daily limits enforced in database (UNIQUE constraints)
✅ **Session Security** - HTTPOnly, Secure, SameSite cookies
✅ **Authorization** - @login_required decorators
✅ **Data Access** - Users can only access their own couple's data

## 📱 PWA Installation

### iPhone (iOS)
1. Open in Safari
2. Tap Share button
3. Select "Add to Home Screen"
4. Name it "LOVIO"

### Android
1. Open in Chrome
2. Tap menu (⋮)
3. Select "Install app"
4. Confirm

## 🗄️ Database Migrations

Create new migration:
```bash
flask db migrate -m "Add new feature"
flask db upgrade
```

## 📊 XP System

**Daily Limits:**
- Check-in: +1 XP (once per day)
- Mood: +3 XP (once per day)
- Activity: +8 XP (once per day)
- Diary: +5 XP (unlimited)
- Goal: +2 XP (unlimited)
- Goal Complete: +25 XP
- Date Accept: +20 XP
- Date Complete: +50 XP
- Habit Complete: +10 XP
- Wish Gift: +30 XP
- Confession: +15 XP

**Relationship Levels:**
1. Newbies (0 XP)
2. In Love (100 XP)
3. Soul Mates (300 XP)
4. Perfect Pair (600 XP)
5. Legendary (1000+ XP)

## 🐛 Troubleshooting

### Database Connection Error
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Run `flask db upgrade` to initialize

### CSRF Token Missing
- Make sure `{{ csrf_token() }}` is in form
- Clear browser cache/cookies

### PWA Not Working
- Check service-worker.js is accessible at `/static/service-worker.js`
- Verify manifest.json path in HTML head
- HTTPS required for PWA (not localhost)

## 📝 API Endpoints

### Auth
- `POST /register` - Create account
- `POST /login` - Login
- `GET /logout` - Logout

### Invitations
- `POST /api/invite/send` - Send invitation
- `POST /api/invite/<id>/accept` - Accept invitation
- `POST /api/invite/<id>/decline` - Decline invitation

### Content
- `POST /api/mood/add` - Add mood (once per day)
- `POST /api/diary/add` - Add diary entry
- `POST /api/activity/select` - Select activity (once per day)
- `POST /api/goals/add` - Create goal
- `POST /api/goals/complete/<id>` - Complete goal
- `POST /api/places/add` - Add place
- `POST /api/places/visit` - Mark place as visited
- `POST /api/dates/add` - Propose date
- `POST /api/dates/<id>/respond` - Accept/decline date
- `POST /api/dates/<id>/complete` - Complete date
- `POST /api/habits/add` - Create habit
- `POST /api/habits/<id>/complete` - Complete habit
- `POST /api/wishes/add` - Add wish
- `POST /api/wishes/gift` - Mark wish as gifted
- `POST /api/confessions/add` - Add confession
- `POST /api/notifications/mark-read` - Mark notification as read

## 📄 License

Proprietary - All Rights Reserved

## 👥 Support

For issues or feature requests, open an issue on GitHub.

---

**LOVIO v2.0** - Premium experience for couples 💕
