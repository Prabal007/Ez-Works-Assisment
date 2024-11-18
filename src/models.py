from src import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_ops_user = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(4), nullable=True)
    

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_data = db.Column(db.LargeBinary, nullable=False)  


class DownloadToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(36), unique=True, nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    expires_at = db.Column(db.DateTime, nullable=False)