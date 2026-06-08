from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import enum

db = SQLAlchemy()

class RelationshipLevel(enum.Enum):
    NEWBIES = 1
    IN_LOVE = 2
    SOUL_MATES = 3
    PERFECT_PAIR = 4
    LEGENDARY = 5

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(10), default='female')  # male, female, other
    language = db.Column(db.String(2), default='en')
    avatar_url = db.Column(db.String(255), default='')
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    last_check_in = db.Column(db.Date)
    xp = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'))
    goals = db.relationship('Goal', backref='creator', lazy='dynamic', cascade='all, delete-orphan')
    places = db.relationship('Place', backref='creator', lazy='dynamic', cascade='all, delete-orphan')
    dates_proposed = db.relationship('DatePlan', backref='proposer', lazy='dynamic', cascade='all, delete-orphan')
    wishes = db.relationship('Wish', backref='creator', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    sent_invitations = db.relationship('CoupleInvitation', foreign_keys='CoupleInvitation.sender_id', 
                                      backref='sender', cascade='all, delete-orphan')
    received_invitations = db.relationship('CoupleInvitation', foreign_keys='CoupleInvitation.receiver_id',
                                          backref='receiver', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_couple(self):
        return self.couple_id is not None
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()

class Couple(db.Model):
    __tablename__ = 'couples'
    
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    xp = db.Column(db.Integer, default=0)
    relationship_level = db.Column(db.Enum(RelationshipLevel), default=RelationshipLevel.NEWBIES)
    closeness = db.Column(db.Integer, default=50)  # 0-100
    couple_since = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user1 = db.relationship('User', foreign_keys=[user1_id])
    user2 = db.relationship('User', foreign_keys=[user2_id])
    goals = db.relationship('Goal', backref='couple', cascade='all, delete-orphan')
    places = db.relationship('Place', backref='couple', cascade='all, delete-orphan')
    dates = db.relationship('DatePlan', backref='couple', cascade='all, delete-orphan')
    wishes = db.relationship('Wish', backref='couple', cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='couple', cascade='all, delete-orphan')
    
    def get_partner(self, current_user_id):
        return User.query.get(self.user2_id if self.user1_id == current_user_id else self.user1_id)
    
    def update_xp(self, amount):
        self.xp += amount
        self.update_level()
        db.session.commit()
    
    def update_level(self):
        xp_thresholds = {
            RelationshipLevel.NEWBIES: 0,
            RelationshipLevel.IN_LOVE: 100,
            RelationshipLevel.SOUL_MATES: 300,
            RelationshipLevel.PERFECT_PAIR: 600,
            RelationshipLevel.LEGENDARY: 1000,
        }
        for level in [RelationshipLevel.LEGENDARY, RelationshipLevel.PERFECT_PAIR, 
                      RelationshipLevel.SOUL_MATES, RelationshipLevel.IN_LOVE]:
            if self.xp >= xp_thresholds[level]:
                self.relationship_level = level
                break

class Goal(db.Model):
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def complete(self):
        self.completed = True
        self.completed_at = datetime.utcnow()
        db.session.commit()

class Place(db.Model):
    __tablename__ = 'places'
    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    visited = db.Column(db.Boolean, default=False)
    visited_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DatePlan(db.Model):
    __tablename__ = 'date_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=False)
    proposer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    planned_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Wish(db.Model):
    __tablename__ = 'wishes'
    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.String(300), nullable=False)
    price = db.Column(db.Integer, default=0)
    gifted = db.Column(db.Boolean, default=False)
    gifted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ImportantDate(db.Model):
    __tablename__ = 'important_dates'

    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    date_value = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task = db.Column(db.String(300), nullable=False)
    activity_date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'activity_date', name='unique_activity_per_day'),
    )

class DailyPromptResponse(db.Model):
    __tablename__ = 'daily_prompt_responses'

    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couples.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_date = db.Column(db.Date, nullable=False)
    question_text = db.Column(db.String(500), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    mood_level = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'question_date', name='unique_daily_prompt_response'),
    )

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notif_type = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CoupleInvitation(db.Model):
    __tablename__ = 'couple_invitations'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)
    
    def accept(self):
        couple = Couple(user1_id=self.sender_id, user2_id=self.receiver_id)
        db.session.add(couple)
        self.status = 'accepted'
        self.responded_at = datetime.utcnow()
        db.session.commit()
        return couple
    
    def decline(self):
        self.status = 'declined'
        self.responded_at = datetime.utcnow()
        db.session.commit()
