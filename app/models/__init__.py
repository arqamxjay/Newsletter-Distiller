"""
Database models for Newsletter Distiller
"""

from flask_login import UserMixin
from datetime import datetime
from app import db, login_manager


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    gmail_token = db.relationship('GmailToken', backref='user', uselist=False, cascade='all, delete-orphan')
    preferences = db.relationship('UserPreferences', backref='user', uselist=False, cascade='all, delete-orphan')
    newsletters = db.relationship('Newsletter', backref='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'


class GmailToken(db.Model):
    """Store Gmail OAuth tokens securely"""
    __tablename__ = 'gmail_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<GmailToken user_id={self.user_id}>'


class UserPreferences(db.Model):
    """User preferences for newsletter processing"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    newsletter_label = db.Column(db.String(255), default='To-Summarize')
    summary_style = db.Column(db.String(50), default='bullet-points')  # 'bullet-points', 'paragraph', 'summary'
    min_length = db.Column(db.Integer, default=5)  # minimum lines for processing
    auto_send = db.Column(db.Boolean, default=False)
    send_to_email = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPreferences user_id={self.user_id}>'


class Newsletter(db.Model):
    """Track processed newsletters"""
    __tablename__ = 'newsletters'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    gmail_message_id = db.Column(db.String(255), nullable=False)
    original_subject = db.Column(db.String(500))
    original_content = db.Column(db.Text)
    cleaned_content = db.Column(db.Text)
    summary = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Newsletter {self.id} user_id={self.user_id}>'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))
