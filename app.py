from datetime import date, datetime, timedelta
from functools import wraps
import os

from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from config import config
from models import (
    Activity,
    Confession,
    Couple,
    CoupleInvitation,
    DatePlan,
    Diary,
    Goal,
    Habit,
    ImportantDate,
    Mood,
    Notification,
    Place,
    User,
    Wish,
    db,
)

load_dotenv()

TRANSLATIONS = {
    'en': {
        'home': 'Home',
        'settings': 'Settings',
        'exit': 'Exit',
        'language': 'Language',
        'english': 'English',
        'russian': 'Russian',
        'save': 'Save',
        'saved': 'Saved',
        'hello': 'Hello',
        'days_together': 'Days Together',
        'memories': 'Memories',
        'closeness': 'Closeness',
        'streak': 'Streak',
        'choose_activity': 'Choose an Activity',
        'diary': 'Diary',
        'mood': 'Mood',
        'goals': 'Goals',
        'places': 'Places',
        'dates': 'Dates',
        'habits': 'Habits',
        'activity': 'Activity',
        'wishes': 'Wishes',
        'confess': 'Confess',
        'important': 'Important',
        'welcome': 'Welcome to LOVIO!',
        'not_in_couple': "You're not in a couple yet. Let's change that!",
        'send_invitation_label': 'Send an invitation to your partner:',
        'partner_username': "Enter partner's username",
        'send_invitation': 'Send Invitation',
        'partner_register_first': 'Your partner needs to be registered first!',
        'profile': 'Profile',
        'username': 'Username',
        'email': 'Email',
        'name': 'Name',
        'total_xp': 'Total XP',
        'couple_status': 'Couple Status',
        'partner': 'Partner',
        'together_since': 'Together since',
        'couple_xp': 'Couple XP',
        'relationship_level': 'Relationship Level',
        'find_partner': 'Find Your Partner',
        'pending_invitations': 'Pending Invitations',
        'accept': 'Accept',
        'decline': 'Decline',
        'log_out': 'Log Out',
    },
    'ru': {
        'home': 'Главная',
        'settings': 'Настройки',
        'exit': 'Выход',
        'language': 'Язык',
        'english': 'Английский',
        'russian': 'Русский',
        'save': 'Сохранить',
        'saved': 'Сохранено',
        'hello': 'Привет',
        'days_together': 'Дней вместе',
        'memories': 'Воспоминания',
        'closeness': 'Близость',
        'streak': 'Серия',
        'choose_activity': 'Выберите раздел',
        'diary': 'Дневник',
        'mood': 'Настроение',
        'goals': 'Цели',
        'places': 'Места',
        'dates': 'Свидания',
        'habits': 'Привычки',
        'activity': 'Активность',
        'wishes': 'Желания',
        'confess': 'Признания',
        'important': 'Важное',
        'welcome': 'Добро пожаловать в LOVIO!',
        'not_in_couple': 'Вы пока не в паре. Давайте это исправим!',
        'send_invitation_label': 'Отправьте приглашение партнёру:',
        'partner_username': 'Введите username партнёра',
        'send_invitation': 'Отправить приглашение',
        'partner_register_first': 'Партнёр должен сначала зарегистрироваться!',
        'profile': 'Профиль',
        'username': 'Username',
        'email': 'Email',
        'name': 'Имя',
        'total_xp': 'Всего XP',
        'couple_status': 'Статус пары',
        'partner': 'Партнёр',
        'together_since': 'Вместе с',
        'couple_xp': 'XP пары',
        'relationship_level': 'Уровень отношений',
        'find_partner': 'Найти партнёра',
        'pending_invitations': 'Ожидающие приглашения',
        'accept': 'Принять',
        'decline': 'Отклонить',
        'log_out': 'Выйти',
    },
}


def create_app(config_name=None):
    config_name = config_name or os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    Migrate(app, db)
    CSRFProtect(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    def current_couple():
        if not current_user.is_authenticated or not current_user.couple_id:
            return None
        return db.session.get(Couple, current_user.couple_id)

    def require_couple_json(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            couple = current_couple()
            if not couple:
                return jsonify({'error': 'Must be in a couple'}), 400
            return f(couple, *args, **kwargs)
        return wrapper

    def partner_for(couple):
        return couple.get_partner(current_user.id)

    def add_notification(user_id, notif_type, text):
        db.session.add(Notification(user_id=user_id, notif_type=notif_type, text=text))

    def notify_partner(couple, notif_type, text):
        partner = partner_for(couple)
        if partner:
            add_notification(partner.id, notif_type, text)

    def mark_section_read(*notif_types):
        if current_user.is_authenticated:
            Notification.query.filter(
                Notification.user_id == current_user.id,
                Notification.notif_type.in_(notif_types),
                Notification.read.is_(False),
            ).update({'read': True}, synchronize_session=False)
            db.session.commit()

    def add_xp(couple, amount):
        current_user.xp += amount
        couple.xp += amount
        couple.update_level()

    def json_data():
        return request.get_json(silent=True) or {}

    def parse_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @app.context_processor
    def inject_globals():
        language = getattr(current_user, 'language', 'en') if current_user.is_authenticated else 'en'
        if language not in TRANSLATIONS:
            language = 'en'
        unread_notifications = []
        notification_counts = {}
        if current_user.is_authenticated:
            unread_notifications = Notification.query.filter_by(
                user_id=current_user.id,
                read=False,
            ).order_by(Notification.created_at.desc()).all()
            for notification in unread_notifications:
                notification_counts[notification.notif_type] = notification_counts.get(notification.notif_type, 0) + 1
        return {
            'unread_notifications': unread_notifications,
            'notification_counts': notification_counts,
            'lang': language,
            'tr': TRANSLATIONS[language],
        }

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            name = request.form.get('name', '').strip()
            gender = request.form.get('gender', 'female')

            if not all([username, email, password, confirm_password, name]):
                flash('All fields are required', 'error')
                return redirect(url_for('register'))
            if len(username) < 3 or len(username) > 80:
                flash('Username must be 3-80 characters', 'error')
                return redirect(url_for('register'))
            if len(password) < 8:
                flash('Password must be at least 8 characters', 'error')
                return redirect(url_for('register'))
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('register'))
            if '@' not in email or len(email) > 120:
                flash('Invalid email', 'error')
                return redirect(url_for('register'))
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
                return redirect(url_for('register'))
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return redirect(url_for('register'))

            user = User(username=username, email=email, name=name, gender=gender)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        return render_template('auth/register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user, remember=bool(request.form.get('remember')))
                user.update_last_login()
                if user.last_check_in != date.today():
                    user.xp += 1
                    user.last_check_in = date.today()
                    db.session.commit()
                next_page = request.args.get('next')
                return redirect(next_page if next_page and next_page.startswith('/') else url_for('dashboard'))

            flash('Invalid username or password', 'error')

        return render_template('auth/login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        couple = current_couple()
        partner = partner_for(couple) if couple else None
        stats = {
            'xp': current_user.xp,
            'streak': calculate_streak(current_user),
            'couple_xp': couple.xp if couple else 0,
            'relationship_level': couple.relationship_level if couple else None,
            'closeness': couple.closeness if couple else 50,
            'days_together': (date.today() - couple.couple_since).days if couple else 0,
            'diary_count': Diary.query.filter_by(couple_id=couple.id).count() if couple else 0,
            'goals_count': Goal.query.filter_by(couple_id=couple.id, completed=True).count() if couple else 0,
            'notifications': Notification.query.filter_by(user_id=current_user.id, read=False).count(),
        }
        return render_template('dashboard.html', partner=partner, **stats)

    @app.route('/diary')
    @login_required
    def diary():
        couple = current_couple()
        if not couple:
            return redirect(url_for('dashboard'))
        mark_section_read('diary')
        diaries = Diary.query.filter_by(couple_id=couple.id).order_by(Diary.created_at.desc()).all()
        return render_template('diary.html', diaries=diaries)

    @app.route('/mood')
    @login_required
    def mood():
        couple = current_couple()
        if not couple:
            return redirect(url_for('dashboard'))
        mark_section_read('mood')
        moods = Mood.query.filter_by(couple_id=couple.id).order_by(Mood.created_at.desc()).all()
        return render_template('mood.html', moods=moods)

    @app.route('/goals')
    @login_required
    def goals():
        couple = current_couple()
        if not couple:
            return redirect(url_for('dashboard'))
        mark_section_read('goal')
        goals_list = Goal.query.filter_by(couple_id=couple.id).order_by(Goal.created_at.desc()).all()
        return render_template('goals.html', goals=goals_list)

    @app.route('/places')
    @login_required
    def places():
        couple = current_couple()
        if not couple:
            return redirect(url_for('dashboard'))
        mark_section_read('place')
        places_list = Place.query.filter_by(couple_id=couple.id).order_by(Place.created_at.desc()).all()
        return render_template('places.html', places=places_list)

    @app.route('/dates')
    @login_required
    def dates():
        couple = current_couple()
        if not couple:
            return redirect(url_for('dashboard'))
        mark_section_read('date')
        dates_list = DatePlan.query.filter_by(couple_id=couple.id).order_by(DatePlan.created_at.desc()).all()
        return render_template('dates.html', dates=dates_list)

    @app.route('/habits')
    @login_required
    def habits():
        couple = current_couple()
        if not couple:
            return redirect(url_for('dashboard'))
        mark_section_read('habit')
        habits_list = Habit.query.filter_by(couple_id=couple.id).order_by(Habit.created_at.desc()).all()
        return render_template('habits.html', habits=habits_list)

    @app.route('/activities')
    @login_required
    def activities():
        couple = current_couple()
        if not couple:
            return redirect(url_for('dashboard'))
        mark_section_read('activity')
        activities_list = Activity.query.filter_by(couple_id=couple.id).order_by(Activity.created_at.desc()).all()
        tasks = [
            'Support your partner',
            'Give them a long hug',
            'Share an intimate moment',
            'Have a deep conversation',
            'Surprise them with a gift',
            'Listen without judging',
            'Cook dinner together',
            'Help with chores',
            'Plan a movie night',
            'Call them just to talk',
        ]
        return render_template('activities.html', activities=activities_list, tasks=tasks)

    @app.route('/wishes')
    @login_required
    def wishes():
        couple = current_couple()
        if not couple:
            return redirect(url_for('dashboard'))
        mark_section_read('wish')
        wishes_list = Wish.query.filter_by(couple_id=couple.id).order_by(Wish.created_at.desc()).all()
        return render_template('wishes.html', wishes=wishes_list)

    @app.route('/confessions')
    @login_required
    def confessions():
        couple = current_couple()
        if not couple:
            return redirect(url_for('dashboard'))
        mark_section_read('confession')
        confessions_list = Confession.query.filter_by(couple_id=couple.id).order_by(Confession.created_at.desc()).all()
        return render_template('confessions.html', confessions=confessions_list)

    @app.route('/important-dates')
    @login_required
    def important_dates():
        couple = current_couple()
        if not couple:
            return redirect(url_for('dashboard'))
        mark_section_read('important_date')
        dates_list = ImportantDate.query.filter_by(couple_id=couple.id).order_by(ImportantDate.date_value.asc()).all()
        return render_template('important-dates.html', important_dates=dates_list)

    @app.route('/settings')
    @login_required
    def settings():
        couple = current_couple()
        partner = partner_for(couple) if couple else None
        pending_invitations = CoupleInvitation.query.filter_by(receiver_id=current_user.id, status='pending').all()
        mark_section_read('invitation', 'couple')
        return render_template(
            'settings.html',
            couple=couple,
            partner=partner,
            pending_invitations=pending_invitations,
        )

    @app.route('/api/invite/send', methods=['POST'])
    @login_required
    def send_invitation():
        if current_user.has_couple():
            return jsonify({'error': 'You are already in a couple'}), 400

        receiver_username = json_data().get('username', '').strip()
        receiver = User.query.filter_by(username=receiver_username).first()
        if not receiver:
            return jsonify({'error': 'User not found'}), 404
        if receiver.id == current_user.id:
            return jsonify({'error': 'Cannot invite yourself'}), 400
        if receiver.has_couple():
            return jsonify({'error': 'User is already in a couple'}), 400

        existing = CoupleInvitation.query.filter_by(
            sender_id=current_user.id,
            receiver_id=receiver.id,
            status='pending',
        ).first()
        if existing:
            return jsonify({'error': 'Invitation already sent'}), 400

        db.session.add(CoupleInvitation(sender_id=current_user.id, receiver_id=receiver.id))
        add_notification(receiver.id, 'invitation', f'{current_user.name} invited you to be partners!')
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/api/settings/language', methods=['POST'])
    @login_required
    def update_language():
        language = json_data().get('language', 'en')
        if language not in TRANSLATIONS:
            return jsonify({'error': 'Invalid language'}), 400
        current_user.language = language
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/api/invite/<int:invitation_id>/accept', methods=['POST'])
    @login_required
    def accept_invitation(invitation_id):
        invitation = db.session.get(CoupleInvitation, invitation_id)
        if not invitation or invitation.receiver_id != current_user.id:
            return jsonify({'error': 'Invalid invitation'}), 404
        if invitation.status != 'pending':
            return jsonify({'error': 'Invitation already processed'}), 400
        if current_user.has_couple() or invitation.sender.has_couple():
            return jsonify({'error': 'One user is already in a couple'}), 400

        couple = invitation.accept()
        sender = db.session.get(User, invitation.sender_id)
        current_user.couple_id = couple.id
        sender.couple_id = couple.id
        add_notification(sender.id, 'couple', f'{current_user.name} accepted your invitation!')
        db.session.commit()
        return jsonify({'success': True, 'couple_id': couple.id})

    @app.route('/api/invite/<int:invitation_id>/decline', methods=['POST'])
    @login_required
    def decline_invitation(invitation_id):
        invitation = db.session.get(CoupleInvitation, invitation_id)
        if not invitation or invitation.receiver_id != current_user.id:
            return jsonify({'error': 'Invalid invitation'}), 404
        if invitation.status != 'pending':
            return jsonify({'error': 'Invitation already processed'}), 400

        invitation.decline()
        add_notification(invitation.sender_id, 'invitation', f'{current_user.name} declined your invitation.')
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/api/mood/add', methods=['POST'])
    @login_required
    @require_couple_json
    def add_mood(couple):
        level = parse_int(json_data().get('level'), 0)
        if level < 1 or level > 10:
            return jsonify({'error': 'Mood must be 1-10'}), 400

        mood = Mood(couple_id=couple.id, author_id=current_user.id, level=level)
        db.session.add(mood)
        add_xp(couple, 3)
        notify_partner(couple, 'mood', f'{current_user.name} shared a new mood')
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'You already submitted mood today'}), 400
        return jsonify({'success': True, 'xp_gained': 3})

    @app.route('/api/diary/add', methods=['POST'])
    @login_required
    @require_couple_json
    def add_diary(couple):
        text = json_data().get('text', '').strip()
        if not text or len(text) > 5000:
            return jsonify({'error': 'Text must be 1-5000 characters'}), 400

        db.session.add(Diary(couple_id=couple.id, author_id=current_user.id, text=text))
        add_xp(couple, 5)
        notify_partner(couple, 'diary', f'{current_user.name} added a new diary entry')
        db.session.commit()
        return jsonify({'success': True, 'xp_gained': 5})

    @app.route('/api/activity/select', methods=['POST'])
    @login_required
    @require_couple_json
    def select_activity(couple):
        task = json_data().get('task', '').strip()
        if not task or len(task) > 300:
            return jsonify({'error': 'Invalid task'}), 400

        db.session.add(Activity(couple_id=couple.id, user_id=current_user.id, task=task))
        add_xp(couple, 8)
        notify_partner(couple, 'activity', f'{current_user.name} selected a new activity')
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({'error': 'You already selected activity today'}), 400
        return jsonify({'success': True, 'xp_gained': 8})

    @app.route('/api/goals/add', methods=['POST'])
    @login_required
    @require_couple_json
    def add_goal(couple):
        text = json_data().get('text', '').strip()
        if not text or len(text) > 500:
            return jsonify({'error': 'Goal must be 1-500 characters'}), 400
        db.session.add(Goal(couple_id=couple.id, creator_id=current_user.id, text=text))
        add_xp(couple, 2)
        notify_partner(couple, 'goal', f'{current_user.name} added a new goal')
        db.session.commit()
        return jsonify({'success': True, 'xp_gained': 2})

    @app.route('/api/goals/complete/<int:goal_id>', methods=['POST'])
    @login_required
    @require_couple_json
    def complete_goal(couple, goal_id):
        goal = Goal.query.filter_by(id=goal_id, couple_id=couple.id).first()
        if not goal:
            return jsonify({'error': 'Goal not found'}), 404
        if not goal.completed:
            goal.completed = True
            goal.completed_at = datetime.utcnow()
            add_xp(couple, 25)
            notify_partner(couple, 'goal', f'{current_user.name} completed a goal')
            db.session.commit()
        return jsonify({'success': True, 'xp_gained': 25})

    @app.route('/api/places/add', methods=['POST'])
    @login_required
    @require_couple_json
    def add_place(couple):
        name = json_data().get('name', '').strip()
        if not name or len(name) > 200:
            return jsonify({'error': 'Place name must be 1-200 characters'}), 400
        db.session.add(Place(couple_id=couple.id, creator_id=current_user.id, name=name))
        add_xp(couple, 2)
        notify_partner(couple, 'place', f'{current_user.name} added a new place')
        db.session.commit()
        return jsonify({'success': True, 'xp_gained': 2})

    @app.route('/api/places/visit', methods=['POST'])
    @login_required
    @require_couple_json
    def visit_place(couple):
        name = json_data().get('name', '').strip()
        place = Place.query.filter_by(couple_id=couple.id, name=name).first()
        if not place:
            return jsonify({'error': 'Place not found'}), 404
        if not place.visited:
            place.visited = True
            place.visited_at = datetime.utcnow()
            add_xp(couple, 10)
            notify_partner(couple, 'place', f'{current_user.name} marked a place as visited')
            db.session.commit()
        return jsonify({'success': True, 'xp_gained': 10})

    @app.route('/api/dates/add', methods=['POST'])
    @login_required
    @require_couple_json
    def add_date(couple):
        data = json_data()
        title = data.get('title', '').strip()
        planned_date = data.get('planned_date', '')
        description = data.get('description', '').strip()
        if not title or len(title) > 200:
            return jsonify({'error': 'Date title must be 1-200 characters'}), 400
        try:
            parsed_date = datetime.fromisoformat(planned_date)
        except ValueError:
            return jsonify({'error': 'Invalid date'}), 400
        date_plan = DatePlan(
            couple_id=couple.id,
            proposer_id=current_user.id,
            title=title,
            description=description[:1000],
            planned_date=parsed_date,
        )
        db.session.add(date_plan)
        add_xp(couple, 5)
        notify_partner(couple, 'date', f'{current_user.name} proposed a new date')
        db.session.commit()
        return jsonify({'success': True, 'xp_gained': 5})

    @app.route('/api/dates/<int:date_id>/respond', methods=['POST'])
    @login_required
    @require_couple_json
    def respond_date(couple, date_id):
        date_plan = DatePlan.query.filter_by(id=date_id, couple_id=couple.id).first()
        status = json_data().get('status')
        if not date_plan:
            return jsonify({'error': 'Date not found'}), 404
        if date_plan.proposer_id == current_user.id:
            return jsonify({'error': 'Only your partner can respond'}), 400
        if status not in {'accepted', 'declined'}:
            return jsonify({'error': 'Invalid status'}), 400
        date_plan.status = status
        if status == 'accepted':
            add_xp(couple, 20)
            add_notification(date_plan.proposer_id, 'date', f'{current_user.name} accepted your date')
        else:
            add_notification(date_plan.proposer_id, 'date', f'{current_user.name} declined your date')
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/api/dates/<int:date_id>/complete', methods=['POST'])
    @login_required
    @require_couple_json
    def complete_date(couple, date_id):
        date_plan = DatePlan.query.filter_by(id=date_id, couple_id=couple.id).first()
        if not date_plan:
            return jsonify({'error': 'Date not found'}), 404
        date_plan.status = 'completed'
        add_xp(couple, 50)
        db.session.commit()
        return jsonify({'success': True, 'xp_gained': 50})

    @app.route('/api/habits/add', methods=['POST'])
    @login_required
    @require_couple_json
    def add_habit(couple):
        text = json_data().get('text', '').strip()
        if not text or len(text) > 300:
            return jsonify({'error': 'Habit must be 1-300 characters'}), 400
        db.session.add(Habit(couple_id=couple.id, creator_id=current_user.id, text=text))
        notify_partner(couple, 'habit', f'{current_user.name} added a new habit')
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/api/habits/complete/<int:habit_id>', methods=['POST'])
    @login_required
    @require_couple_json
    def complete_habit(couple, habit_id):
        habit = Habit.query.filter_by(id=habit_id, couple_id=couple.id).first()
        if not habit:
            return jsonify({'error': 'Habit not found'}), 404
        if habit.last_completed == date.today():
            return jsonify({'error': 'Habit already completed today'}), 400
        habit.streak = habit.streak + 1 if habit.last_completed == date.today() - timedelta(days=1) else 1
        habit.last_completed = date.today()
        add_xp(couple, 10)
        notify_partner(couple, 'habit', f'{current_user.name} completed a habit')
        db.session.commit()
        return jsonify({'success': True, 'xp_gained': 10})

    @app.route('/api/wishes/add', methods=['POST'])
    @login_required
    @require_couple_json
    def add_wish(couple):
        data = json_data()
        text = data.get('text', '').strip()
        price = max(0, parse_int(data.get('price'), 0))
        if not text or len(text) > 300:
            return jsonify({'error': 'Wish must be 1-300 characters'}), 400
        db.session.add(Wish(couple_id=couple.id, creator_id=current_user.id, text=text, price=price))
        add_xp(couple, 2)
        notify_partner(couple, 'wish', f'{current_user.name} added a new wish')
        db.session.commit()
        return jsonify({'success': True, 'xp_gained': 2})

    @app.route('/api/wishes/gift', methods=['POST'])
    @login_required
    @require_couple_json
    def gift_wish(couple):
        text = json_data().get('text', '').strip()
        wish = Wish.query.filter_by(couple_id=couple.id, text=text).first()
        if not wish:
            return jsonify({'error': 'Wish not found'}), 404
        if not wish.gifted:
            wish.gifted = True
            wish.gifted_at = datetime.utcnow()
            add_xp(couple, 30)
            notify_partner(couple, 'wish', f'{current_user.name} marked a wish as gifted')
            db.session.commit()
        return jsonify({'success': True, 'xp_gained': 30})

    @app.route('/api/confessions/add', methods=['POST'])
    @login_required
    @require_couple_json
    def add_confession(couple):
        text = json_data().get('text', '').strip()
        if not text or len(text) > 5000:
            return jsonify({'error': 'Confession must be 1-5000 characters'}), 400
        db.session.add(Confession(couple_id=couple.id, author_id=current_user.id, text=text))
        add_xp(couple, 15)
        notify_partner(couple, 'confession', f'{current_user.name} sent a new confession')
        db.session.commit()
        return jsonify({'success': True, 'xp_gained': 15})

    @app.route('/api/important-dates/add', methods=['POST'])
    @login_required
    @require_couple_json
    def add_important_date(couple):
        data = json_data()
        title = data.get('title', '').strip()
        raw_date = data.get('date', '')
        if not title or len(title) > 200:
            return jsonify({'error': 'Title must be 1-200 characters'}), 400
        try:
            parsed_date = date.fromisoformat(raw_date)
        except ValueError:
            return jsonify({'error': 'Invalid date'}), 400
        db.session.add(ImportantDate(
            couple_id=couple.id,
            creator_id=current_user.id,
            title=title,
            date_value=parsed_date,
        ))
        notify_partner(couple, 'important_date', f'{current_user.name} added an important date')
        db.session.commit()
        return jsonify({'success': True})

    @app.route('/api/notifications/mark-read', methods=['POST'])
    @login_required
    def mark_notifications_read():
        Notification.query.filter_by(user_id=current_user.id, read=False).update({'read': True})
        db.session.commit()
        return jsonify({'success': True})

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.cli.command()
    def init_db():
        db.create_all()
        print('Database initialized.')

    @app.cli.command()
    def seed_db():
        if User.query.first():
            print('Database already has data.')
            return
        user1 = User(username='alice', email='alice@example.com', name='Alice', gender='female')
        user1.set_password('password123')
        user2 = User(username='bob', email='bob@example.com', name='Bob', gender='male')
        user2.set_password('password123')
        db.session.add_all([user1, user2])
        db.session.commit()
        print('Sample users created.')

    with app.app_context():
        db.create_all()
        ensure_schema()

    return app


def ensure_schema():
    if db.engine.dialect.name != 'sqlite':
        return
    columns = {
        row[1]
        for row in db.session.execute(text('PRAGMA table_info(users)')).fetchall()
    }
    if 'language' not in columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR(2) DEFAULT 'en'"))
        db.session.commit()


def calculate_streak(user):
    if not user.has_couple():
        return 0

    couple = db.session.get(Couple, user.couple_id)
    if not couple:
        return 0

    streak = 0
    current_date = date.today()
    while Activity.query.filter_by(
        user_id=user.id,
        couple_id=couple.id,
        activity_date=current_date,
    ).first():
        streak += 1
        current_date -= timedelta(days=1)
    return streak


app = create_app(os.getenv('FLASK_ENV', 'production'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
