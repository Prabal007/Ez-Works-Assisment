from src import db, mail
from flask import request, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
import uuid
from functools import wraps
from src.models import User, File, DownloadToken
from flask import Blueprint
from flask_mail import Message
import random
from flask import url_for
import io
simple_page = Blueprint("simple_page" , __name__)
 

# Helper functions
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, "secret_key",   algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def generate_encrypted_url(file_id):
    unique_string = f"{file_id}-{uuid.uuid4()}"
    return jwt.encode({'file_id': file_id, 'unique_string': unique_string}, "secret_key", algorithm='HS256')


def cleanup_expired_tokens():
    expired_tokens = DownloadToken.query.filter(
        DownloadToken.expires_at < datetime.utcnow()
    ).all()
    
    for token in expired_tokens:
        db.session.delete(token)
    
    db.session.commit()

def generate_verification_code():
     
    return str(random.randint(1000, 9999))


def send_verification_email(to_email, code):
    msg = Message("Email Verification", recipients=[to_email])
    msg.body = f"Please use this code for verification: {code}"
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

# Routes
@simple_page.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_ops_user = data.get("ops_user", False)

    db.session.query(User).delete()   
    db.session.commit()
 

   
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    new_user.is_ops_user = is_ops_user
    db.session.add(new_user)
    db.session.commit()

 
    verification_code = generate_verification_code()
    print(verification_code)
    new_user.verification_code = verification_code
    
    db.session.commit()

    send_verification_email(new_user.email, verification_code)

    return jsonify({'message': 'User created successfully! A verification code has been sent to your email.'})


@simple_page.route('/verify_email', methods=['POST'])
def verify_email():
    data = request.json
    email = data.get('email')
    verification_code = data.get('verification_code')
 
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User not found!'}), 404

     
    if user.verification_code == verification_code:
       
        user.verification_code = None  
        user.email_verified = True
        db.session.commit()
        return jsonify({'message': 'Email verified successfully!'})

    return jsonify({'message': 'Invalid verification code!'}), 400


@simple_page.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email , email_verified = True).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials!'}), 401

    token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                       "secret_key", algorithm='HS256')
    return jsonify({"message": "Login successful", 'token': token})

import uuid
from werkzeug.utils import secure_filename

def allowed_extension(filename):
    return filename.rsplit('.', 1)[1].lower() in ['pptx', 'docx', 'xlsx']


@simple_page.route('/upload', methods=['POST'])
@token_required
def upload_file(current_user):
    
    if not current_user.is_ops_user:
        return jsonify({'message': 'Permission denied!'}), 403
        
    if 'file' not in request.files:
        return jsonify({'message': 'No file part!'}), 400
        
    file = request.files['file']
    if not file:
        return jsonify({'message': 'No file uploaded!'}), 400
    
    
    original_filename = secure_filename(file.filename)
    
     
    if not allowed_extension(original_filename):
        return jsonify({
            'message': 'Invalid file type! Only PPTX, DOCX, and XLSX files are allowed.'
        }), 400
    
     
    file_data = file.read()
    
  
    filename = f"{uuid.uuid4()}-{original_filename}"
     
    try:
        new_file = File(
            filename=filename,
            uploader_id=current_user.id,
            file_data=file_data
        )
        
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully!',
            'file_id': new_file.id,
            'filename': filename
        })
        
    except Exception as e:
        db.session.rollback()
         
        return jsonify({
            'message': 'An error occurred while saving the file.'
        }), 500

 
@simple_page.route('/download', methods=['GET'])
def download_file():
    token = request.args.get('token')
    if not token:
        return jsonify({'message': 'No download token provided!'}), 400
    
    
    token_record = DownloadToken.query.filter_by(token=token).first()
    if not token_record:
        return jsonify({'message': 'Invalid download token!'}), 404
    
   
    if datetime.datetime.utcnow() > token_record.expires_at:
         
        db.session.delete(token_record)
        db.session.commit()
        return jsonify({'message': 'Download link has expired!'}), 410
    
   
    file_record = File.query.get(token_record.file_id)
    if not file_record:
        return jsonify({'message': 'File not found!'}), 404
    
    
    db.session.delete(token_record)
    db.session.commit()
    
    return send_file(
        io.BytesIO(file_record.file_data),
        download_name=file_record.filename,
        as_attachment=True
    )

 
@simple_page.route('/files/<int:file_id>/get-download-url', methods=['POST'])
@token_required
def generate_download_url(current_user, file_id):
    if current_user.is_ops_user:
        return jsonify({'message': 'Permission denied!'}), 403
    
   
    file_record = File.query.get_or_404(file_id)
    
     
    download_token = str(uuid.uuid4())
     
    token_record = DownloadToken(
        token=download_token,
        file_id=file_id,
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    )
    
    db.session.add(token_record)
    db.session.commit()
    
    
    download_url = url_for(
        'simple_page.download_file',
        token=download_token,
        _external=True
    )
    
    return jsonify({
        'download_url': download_url,
        'expires_at': token_record.expires_at.isoformat()
    })


@simple_page.route('/files', methods=['GET'])
@token_required
def list_files(current_user):
    if not current_user.is_ops_user:
        return jsonify({'message': 'Permission denied!'}), 403
    
     
    files_query = File.query.order_by(File.id.desc())
    
    
    search = request.args.get('search', '')
    if search:
        files_query = files_query.filter(File.filename.ilike(f'%{search}%'))
    
    
    files = files_query.all()
    
     
    files_list = [{
        'id': file.id,
        'filename': file.filename,
        'uploader_id': file.uploader_id,
        'size': len(file.file_data),   
        'file_type': get_file_type(file.filename)
    } for file in files]
    
    return jsonify({
        'files': files_list,
        'total_files': len(files_list)
    })


 
def get_file_type(filename):
    extension = filename.rsplit('.', 1)[-1].lower()
    file_types = {
        'pptx': 'PowerPoint Presentation',
        'docx': 'Word Document',
        'xlsx': 'Excel Spreadsheet'
    }
    return file_types.get(extension, 'Unknown')

@simple_page.route('/')
def home():
    return "Hello, Flask!"
