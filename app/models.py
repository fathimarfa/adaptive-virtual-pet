from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pin_hash = db.Column(db.String(256), nullable=True)
    theme = db.Column(db.String(20), default='normal')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pet = db.relationship('Pet', backref='owner', uselist=False)

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(80), default='Buddy')
    state = db.Column(db.String(32), default='idle')
    hunger = db.Column(db.Integer, default=50)   # 0-100
    mood = db.Column(db.Integer, default=70)     # 0-100
    energy = db.Column(db.Integer, default=80)   # 0-100
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    memory = db.Column(db.Text, default='')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(10))   # 'user' or 'pet'
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

