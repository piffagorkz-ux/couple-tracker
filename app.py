from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, date, timedelta
from functools import wraps
from config import config
from models import db, User, Couple, Goal, Diary, Mood, Place, DatePlan, Habit, Wish, Confession, Activity, Notification, CoupleInvitation, RelationshipLevel
import os

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Инициализация расширений
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    login_manager = LoginManager(app)
    
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # ==================== AUTH ROUTES ====================
    
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
            
            # Валидация
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
            
            # Проверка уникальности
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return redirect(url_for('register'))
            
            # Создание пользователя
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
            
            if not username or not password:
                flash('Username and password are required', 'error')
                return redirect(url_for('login'))
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user, remember=request.form.get('remember'))
                user.update_last_login()
                
                # Check-in reward (только один раз в день)
                if user.last_check_in != date.today():
                    user.xp += 1
                    user.last_check_in = date.today()
                    db.session.commit()
                
                next_page = request.args.get('next')
                if next_page and not next_page.startswith('/'):
                    next_page = None
                
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        
        return render_template('auth/login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    
    # ==================== DASHBOARD ====================
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        user = current_user
        couple = user.couple_data[0] if user.couple_data else None
        partner = None
        stats = {
            'xp': user.xp,
            'streak': calculate_streak(user),
            'couple_xp': couple.xp if couple else 0,
            'relationship_level': couple.relationship_level if couple else None,
            'closeness': couple.closeness if couple else 50,
            'days_together': (date.today() - couple.couple_since).days if couple else 0,
        }
        
        if couple:
            partner = couple.get_partner(user.id)
            last_activity = Activity.query.filter_by(couple_id=couple.id).order_by(Activity.created_at.desc()).first()
            stats['last_activity'] = last_activity.user.name if last_activity else None
            stats['diary_count'] = Diary.query.filter_by(couple_id=couple.id).count()
            stats['goals_count'] = Goal.query.filter_by(couple_id=couple.id, completed=True).count()
            stats['notifications'] = Notification.query.filter_by(user_id=user.id, read=False).count()
        
        return render_template('dashboard.html', partner=partner, **stats)
    
    # ==================== COUPLE SYSTEM ====================
    
    @app.route('/api/invite/send', methods=['POST'])
    @login_required
    def send_invitation():
        if current_user.has_couple():
            return jsonify({'error': 'You are already in a couple'}), 400
        
        data = request.get_json()
        receiver_username = data.get('username', '').strip()
        
        if not receiver_username:
            return jsonify({'error': 'Username required'}), 400
        
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
            status='pending'
        ).first()
        
        if existing:
            return jsonify({'error': 'Invitation already sent'}), 400
        
        invitation = CoupleInvitation(sender_id=current_user.id, receiver_id=receiver.id)
        db.session.add(invitation)
        db.session.commit()
        
        notification = Notification(
            user_id=receiver.id,
            notif_type='invitation',
            text=f'{current_user.name} invited you to be partners!'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True})
    
    @app.route('/api/invite/<int:invitation_id>/accept', methods=['POST'])
    @login_required
    def accept_invitation(invitation_id):
        invitation = CoupleInvitation.query.get(invitation_id)
        
        if not invitation or invitation.receiver_id != current_user.id:
            return jsonify({'error': 'Invalid invitation'}), 404
        
        if invitation.status != 'pending':
            return jsonify({'error': 'Invitation already processed'}), 400
        
        couple = invitation.accept()
        
        # Update both users
        sender = User.query.get(invitation.sender_id)
        current_user.couple_id = couple.id
        sender.couple_id = couple.id
        db.session.commit()
        
        notification = Notification(
            user_id=sender.id,
            notif_type='couple',
            text=f'{current_user.name} accepted your invitation!'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True, 'couple_id': couple.id})
    
    @app.route('/api/invite/<int:invitation_id>/decline', methods=['POST'])
    @login_required
    def decline_invitation(invitation_id):
        invitation = CoupleInvitation.query.get(invitation_id)
        
        if not invitation or invitation.receiver_id != current_user.id:
            return jsonify({'error': 'Invalid invitation'}), 404
        
        if invitation.status != 'pending':
            return jsonify({'error': 'Invitation already processed'}), 400
        
        invitation.decline()
        
        notification = Notification(
            user_id=invitation.sender_id,
            notif_type='invitation',
            text=f'{current_user.name} declined your invitation.'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True})
    
    # ==================== XP PROTECTED ENDPOINTS ====================
    
    def xp_check(xp_amount):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.has_couple():
                    return jsonify({'error': 'Must be in a couple'}), 400
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    @app.route('/api/mood/add', methods=['POST'])
    @login_required
    @xp_check(3)
    def add_mood():
        data = request.get_json()
        level = data.get('level', 5)
        
        if not isinstance(level, int) or level < 1 or level > 10:
            return jsonify({'error': 'Mood must be 1-10'}), 400
        
        couple = current_user.couple_data[0]
        
        # Проверка: только 1 раз в день
        existing_mood = Mood.query.filter_by(
            author_id=current_user.id,
            mood_date=date.today()
        ).first()
        
        if existing_mood:
            return jsonify({'error': 'You already submitted mood today'}), 400
        
        mood = Mood(couple_id=couple.id, author_id=current_user.id, level=level)
        db.session.add(mood)
        
        couple.update_xp(3)
        
        partner = couple.get_partner(current_user.id)
        notification = Notification(
            user_id=partner.id,
            notif_type='mood',
            text=f'{current_user.name} shared their mood'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True, 'xp_gained': 3})
    
    @app.route('/api/diary/add', methods=['POST'])
    @login_required
    @xp_check(5)
    def add_diary():
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text or len(text) > 5000:
            return jsonify({'error': 'Text must be 1-5000 characters'}), 400
        
        couple = current_user.couple_data[0]
        diary = Diary(couple_id=couple.id, author_id=current_user.id, text=text)
        db.session.add(diary)
        
        couple.update_xp(5)
        
        partner = couple.get_partner(current_user.id)
        notification = Notification(
            user_id=partner.id,
            notif_type='diary',
            text=f'{current_user.name} wrote a diary entry'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True, 'xp_gained': 5})
    
    @app.route('/api/activity/select', methods=['POST'])
    @login_required
    @xp_check(8)
    def select_activity():
        data = request.get_json()
        task = data.get('task', '').strip()
        
        if not task or len(task) > 300:
            return jsonify({'error': 'Invalid task'}), 400
        
        couple = current_user.couple_data[0]
        
        # Проверка: только 1 раз в день
        existing = Activity.query.filter_by(
            user_id=current_user.id,
            activity_date=date.today()
        ).first()
        
        if existing:
            return jsonify({'error': 'You already selected activity today'}), 400
        
        activity = Activity(couple_id=couple.id, user_id=current_user.id, task=task)
        db.session.add(activity)
        
        couple.update_xp(8)
        
        partner = couple.get_partner(current_user.id)
        notification = Notification(
            user_id=partner.id,
            notif_type='activity',
            text=f'{current_user.name} selected: {task}'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'success': True, 'xp_gained': 8})
    
    # ==================== ERROR HANDLERS ====================
    
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
    
    # ==================== CLI COMMANDS ====================
    
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print('Database initialized.')
    
    @app.cli.command()
    def seed_db():
        """Seed database with sample data."""
        if User.query.first():
            print('Database already has data.')
            return
        
        user1 = User(username='alice', email='alice@example.com', name='Alice', gender='female')
        user1.set_password('password123')
        
        user2 = User(username='bob', email='bob@example.com', name='Bob', gender='male')
        user2.set_password('password123')
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        print('Sample users created.')
    
    with app.app_context():
        db.create_all()
    
    return app

def calculate_streak(user):
    """Calculate user's activity streak."""
    if not user.has_couple():
        return 0
    
    couple = user.couple_data[0]
    today = date.today()
    streak = 0
    current_date = today
    
    while True:
        activity = Activity.query.filter_by(
            user_id=user.id,
            couple_id=couple.id,
            activity_date=current_date
        ).first()
        
        if not activity:
            break
        
        streak += 1
        current_date -= timedelta(days=1)
    
    return streak

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

    # ==================== PAGES ====================
    
    @app.route('/diary')
    @login_required
    def diary():
        if not current_user.has_couple():
            return redirect(url_for('dashboard'))
        couple = current_user.couple_data[0]
        diaries = Diary.query.filter_by(couple_id=couple.id).order_by(Diary.created_at.desc()).all()
        return render_template('diary.html', diaries=diaries)
    
    @app.route('/mood')
    @login_required
    def mood():
        if not current_user.has_couple():
            return redirect(url_for('dashboard'))
        couple = current_user.couple_data[0]
        moods = Mood.query.filter_by(couple_id=couple.id).order_by(Mood.created_at.desc()).all()
        return render_template('mood.html', moods=moods)
    
    @app.route('/goals')
    @login_required
    def goals():
        if not current_user.has_couple():
            return redirect(url_for('dashboard'))
        couple = current_user.couple_data[0]
        goals_list = Goal.query.filter_by(couple_id=couple.id).order_by(Goal.created_at.desc()).all()
        return render_template('goals.html', goals=goals_list)
    
    @app.route('/places')
    @login_required
    def places():
        if not current_user.has_couple():
            return redirect(url_for('dashboard'))
        couple = current_user.couple_data[0]
        places_list = Place.query.filter_by(couple_id=couple.id).order_by(Place.created_at.desc()).all()
        return render_template('places.html', places=places_list)
    
    @app.route('/dates')
    @login_required
    def dates():
        if not current_user.has_couple():
            return redirect(url_for('dashboard'))
        couple = current_user.couple_data[0]
        dates_list = DatePlan.query.filter_by(couple_id=couple.id).order_by(DatePlan.created_at.desc()).all()
        return render_template('dates.html', dates=dates_list)
    
    @app.route('/habits')
    @login_required
    def habits():
        if not current_user.has_couple():
            return redirect(url_for('dashboard'))
        couple = current_user.couple_data[0]
        habits_list = Habit.query.filter_by(couple_id=couple.id).order_by(Habit.created_at.desc()).all()
        return render_template('habits.html', habits=habits_list)
    
    @app.route('/activities')
    @login_required
    def activities():
        if not current_user.has_couple():
            return redirect(url_for('dashboard'))
        couple = current_user.couple_data[0]
        activities_list = Activity.query.filter_by(couple_id=couple.id).order_by(Activity.created_at.desc()).all()
        
        # Daily task ideas
        tasks = [
            "💪 Support your partner",
            "🤗 Give them a long hug",
            "❤️ Share intimate moment",
            "💬 Have deep conversation",
            "🎁 Surprise them with gift",
            "👂 Listen without judging",
            "🍽️ Cook them dinner",
            "🧼 Help with chores",
            "🎬 Movie night together",
            "📞 Call them just to talk"
        ] if current_user.gender == 'male' else [
            "💋 Give them compliment",
            "💋 Plan romantic date",
            "🌹 Get them flowers",
            "💌 Write love letter",
            "🎀 Surprise gift",
            "🎬 Movie together",
            "🍽️ Cook together",
            "💄 Dress up nicely",
            "💃 Dance together",
            "🎵 Sing their favorite song"
        ]
        
        return render_template('activities.html', activities=activities_list, tasks=tasks)
    
    @app.route('/wishes')
    @login_required
    def wishes():
        if not current_user.has_couple():
            return redirect(url_for('dashboard'))
        couple = current_user.couple_data[0]
        wishes_list = Wish.query.filter_by(couple_id=couple.id).order_by(Wish.created_at.desc()).all()
        return render_template('wishes.html', wishes=wishes_list)
    
    @app.route('/confessions')
    @login_required
    def confessions():
        if not current_user.has_couple():
            return redirect(url_for('dashboard'))
        couple = current_user.couple_data[0]
        confessions_list = Confession.query.filter_by(couple_id=couple.id).order_by(Confession.created_at.desc()).all()
        return render_template('confessions.html', confessions=confessions_list)
    
    @app.route('/important-dates')
    @login_required
    def important_dates():
        if not current_user.has_couple():
            return redirect(url_for('dashboard'))
        return render_template('important-dates.html')
    
    @app.route('/settings')
    @login_required
    def settings():
        couple = current_user.couple_data[0] if current_user.couple_data else None
        partner = couple.get_partner(current_user.id) if couple else None
        pending_invitations = CoupleInvitation.query.filter_by(receiver_id=current_user.id, status='pending').all()
        return render_template('settings.html', couple=couple, partner=partner, pending_invitations=pending_invitations)

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
