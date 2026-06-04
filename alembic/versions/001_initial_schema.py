"""Initial schema creation

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(80), nullable=False, unique=True),
        sa.Column('email', sa.String(120), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('gender', sa.String(10), default='female'),
        sa.Column('avatar_url', sa.String(255), default=''),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('last_check_in', sa.Date(), nullable=True),
        sa.Column('xp', sa.Integer(), default=0),
        sa.Column('couple_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_users_username', 'username'),
        sa.Index('ix_users_email', 'email'),
    )
    
    # Couples table
    op.create_table(
        'couples',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user1_id', sa.Integer(), nullable=False),
        sa.Column('user2_id', sa.Integer(), nullable=False),
        sa.Column('xp', sa.Integer(), default=0),
        sa.Column('relationship_level', sa.String(20), default='NEWBIES'),
        sa.Column('closeness', sa.Integer(), default=50),
        sa.Column('couple_since', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ),
    )
    
    # Goals table
    op.create_table(
        'goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('couple_id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(500), nullable=False),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Diary table
    op.create_table(
        'diaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('couple_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Moods table
    op.create_table(
        'moods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('couple_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('mood_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('author_id', 'mood_date', name='unique_mood_per_day'),
    )
    
    # Places table
    op.create_table(
        'places',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('couple_id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('visited', sa.Boolean(), default=False),
        sa.Column('visited_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # DatePlans table
    op.create_table(
        'date_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('couple_id', sa.Integer(), nullable=False),
        sa.Column('proposer_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), default=''),
        sa.Column('planned_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['proposer_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Habits table
    op.create_table(
        'habits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('couple_id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(300), nullable=False),
        sa.Column('streak', sa.Integer(), default=0),
        sa.Column('last_completed', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Wishes table
    op.create_table(
        'wishes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('couple_id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(300), nullable=False),
        sa.Column('price', sa.Integer(), default=0),
        sa.Column('gifted', sa.Boolean(), default=False),
        sa.Column('gifted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Confessions table
    op.create_table(
        'confessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('couple_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Activities table
    op.create_table(
        'activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('couple_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task', sa.String(300), nullable=False),
        sa.Column('activity_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['couple_id'], ['couples.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'activity_date', name='unique_activity_per_day'),
    )
    
    # Notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notif_type', sa.String(50), nullable=False),
        sa.Column('text', sa.String(500), nullable=False),
        sa.Column('read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # CoupleInvitations table
    op.create_table(
        'couple_invitations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('receiver_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE'),
    )
    
    # Add foreign key for users.couple_id
    op.create_foreign_key('fk_users_couple_id', 'users', 'couples', ['couple_id'], ['id'], ondelete='SET NULL')

def downgrade():
    op.drop_constraint('fk_users_couple_id', 'users')
    op.drop_table('couple_invitations')
    op.drop_table('notifications')
    op.drop_table('activities')
    op.drop_table('confessions')
    op.drop_table('wishes')
    op.drop_table('habits')
    op.drop_table('date_plans')
    op.drop_table('places')
    op.drop_table('moods')
    op.drop_table('diaries')
    op.drop_table('goals')
    op.drop_table('couples')
    op.drop_table('users')
