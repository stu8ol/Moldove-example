from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask_login import UserMixin
from app import login
import os
from flask import current_app

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    games_played = db.Column(db.Integer, default=0)
    games_lost = db.Column(db.Integer, default=0)
    shots_done = db.Column(db.Integer, default=0)
    
    avatar_path =  db.Column(db.String(120), default='/static/users/blank.png')

    def __repr__(self):
        return '<User {}>'.format(self.username)
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  
        
    def avatar(self):
    	return self.avatar_path
    	
    def new_avatar(self, name):
    	self.avatar_path = '/static/users/'+ name
    	print('Profile pic storage', current_app.config['UPLOADED_PHOTOS_DEST'])
    	db.session.commit()
        
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

        
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
