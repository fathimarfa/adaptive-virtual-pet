import os, cv2, base64, numpy as np
from flask import render_template, redirect, url_for, session, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from deepface import DeepFace
from app.auth import auth_bp
from app import db
from app.models import User, Pet

FACES_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'faces')
os.makedirs(FACES_DIR, exist_ok=True)

def save_face_image(username, b64_data):
    header, data = b64_data.split(',', 1)
    img_bytes = base64.b64decode(data)
    arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    path = os.path.join(FACES_DIR, f"{username}.jpg")
    cv2.imwrite(path, img)
    return path

def verify_face(b64_data):
    header, data = b64_data.split(',', 1)
    img_bytes = base64.b64decode(data)
    arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    tmp_path = os.path.join(FACES_DIR, '_tmp_login.jpg')
    cv2.imwrite(tmp_path, img)
    for fname in os.listdir(FACES_DIR):
        if fname.startswith('_') or not fname.endswith('.jpg'):
            continue
        stored_path = os.path.join(FACES_DIR, fname)
        try:
            result = DeepFace.verify(tmp_path, stored_path, enforce_detection=False)
            if result['verified']:
                os.remove(tmp_path)
                return fname.replace('.jpg', '')
        except Exception:
            continue
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    return None

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET'])
def register():
    return render_template('auth/register.html')

@auth_bp.route('/register', methods=['POST'])
def register_post():
    data = request.get_json()
    username = data.get('username', '').strip()
    pin = data.get('pin', '').strip()
    image_b64 = data.get('image')
    theme = data.get('theme', 'normal')
    if not username or not image_b64:
        return jsonify({'success': False, 'message': 'Username and face photo required.'})
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Username already taken.'})
    save_face_image(username, image_b64)
    user = User(username=username, pin_hash=generate_password_hash(pin) if pin else None, theme=theme)
    db.session.add(user)
    db.session.flush()
    pet = Pet(user_id=user.id, name='Buddy')
    db.session.add(pet)
    db.session.commit()
    return jsonify({'success': True})

@auth_bp.route('/login', methods=['GET'])
def login():
    return render_template('auth/login.html')

@auth_bp.route('/login/face', methods=['POST'])
def login_face():
    data = request.get_json()
    image_b64 = data.get('image')
    if not image_b64:
        return jsonify({'success': False, 'message': 'No image received.'})
    username = verify_face(image_b64)
    if not username:
        return jsonify({'success': False, 'message': 'Face not recognised. Try PIN login.'})
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'})
    session['user_id'] = user.id
    session['username'] = user.username
    session['theme'] = user.theme
    return jsonify({'success': True})

@auth_bp.route('/login/pin', methods=['POST'])
def login_pin():
    data = request.get_json()
    username = data.get('username', '').strip()
    pin = data.get('pin', '').strip()
    user = User.query.filter_by(username=username).first()
    if not user or not user.pin_hash:
        return jsonify({'success': False, 'message': 'User not found or no PIN set.'})
    if not check_password_hash(user.pin_hash, pin):
        return jsonify({'success': False, 'message': 'Wrong PIN.'})
    session['user_id'] = user.id
    session['username'] = user.username
    session['theme'] = user.theme
    return jsonify({'success': True})

@auth_bp.route('/logout')
def logout():
    pet = None
    if 'user_id' in session:
        from app.models import Pet
        pet = Pet.query.filter_by(user_id=session['user_id']).first()
    pet_name = pet.name if pet else 'Buddy'
    session.clear()
    return render_template('auth/logout.html', pet_name=pet_name)
