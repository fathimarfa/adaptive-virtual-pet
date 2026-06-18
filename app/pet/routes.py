import os, base64, numpy as np, cv2
from datetime import datetime, timedelta
from flask import render_template, session, redirect, url_for, request, jsonify
from app.pet import pet_bp
from app import db
from app.models import Pet, User, ChatHistory
from app.pet.fsm import PetFSM
from app.pet.llm import get_pet_response
from deepface import DeepFace

XP_PER_MESSAGE = 10
XP_PER_LEVEL   = 100  # every 100 XP = level up, max level 5

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def add_xp(pet, amount):
    """Add XP and level up if threshold reached. Returns True if levelled up."""
    pet.xp += amount
    new_level = min(5, 1 + pet.xp // XP_PER_LEVEL)
    levelled_up = new_level > pet.level
    pet.level = new_level
    return levelled_up

def decay_stats(pet):
    """Decay hunger and energy based on time since last update."""
    now = datetime.utcnow()
    minutes = (now - pet.updated_at).total_seconds() / 60
    # lose ~5 hunger and 3 energy per hour
    hunger_loss = int(minutes * 5 / 60)
    energy_loss = int(minutes * 3 / 60)
    pet.hunger = max(0, pet.hunger - hunger_loss)
    pet.energy = max(0, pet.energy - energy_loss)
    pet.updated_at = now

    # auto-trigger FSM if stats critical
    fsm = PetFSM(initial_state=pet.state)
    if pet.hunger <= 20:
        fsm.get_hungry()
    elif pet.energy <= 20:
        fsm.get_sleepy()
    pet.state = fsm.get_state()

@pet_bp.route('/')
@login_required
def home():
    pet = Pet.query.filter_by(user_id=session['user_id']).first()
    user = User.query.get(session['user_id'])
    decay_stats(pet)
    db.session.commit()
    theme = session.get('theme', user.theme or 'normal')
    # load last 20 chat messages
    history = ChatHistory.query.filter_by(user_id=session['user_id'])\
        .order_by(ChatHistory.created_at.desc()).limit(20).all()
    history = list(reversed(history))
    xp_for_next = XP_PER_LEVEL - (pet.xp % XP_PER_LEVEL)
    xp_progress = (pet.xp % XP_PER_LEVEL) * 100 // XP_PER_LEVEL
    return render_template('pet/home.html',
        pet=pet, username=session['username'], theme=theme,
        history=history, xp_progress=xp_progress, xp_for_next=xp_for_next)

@pet_bp.route('/emotion', methods=['POST'])
@login_required
def detect_emotion():
    data = request.get_json()
    image_b64 = data.get('image')
    if not image_b64:
        return jsonify({'error': 'No image'}), 400
    header, raw = image_b64.split(',', 1)
    arr = np.frombuffer(base64.b64decode(raw), np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    tmp = 'tmp_emotion.jpg'
    cv2.imwrite(tmp, img)
    try:
        result = DeepFace.analyze(tmp, actions=['emotion'], enforce_detection=False)
        dominant = result[0]['dominant_emotion']
    except Exception:
        dominant = 'neutral'
    finally:
        if os.path.exists(tmp): os.remove(tmp)

    pet = Pet.query.filter_by(user_id=session['user_id']).first()
    fsm = PetFSM(initial_state=pet.state)
    emotion_map = {
        'happy': 'play', 'surprise': 'play',
        'sad': 'feel_sad', 'angry': 'feel_sad',
        'fear': 'feel_sad', 'disgust': 'feel_sad',
        'neutral': 'calm_down',
    }
    # only apply emotion trigger if stats are not critical
    if pet.hunger > 20 and pet.energy > 20:
        trigger = emotion_map.get(dominant)
        if trigger:
            getattr(fsm, trigger)()
        pet.state = fsm.get_state()
    db.session.commit()
    return jsonify({
        'emotion': dominant,
        'pet_state': pet.state,
        'hunger': pet.hunger,
        'mood': pet.mood,
        'energy': pet.energy
    })

@pet_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    emotion = data.get('emotion', 'neutral')
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    pet = Pet.query.filter_by(user_id=session['user_id']).first()
    levelled_up = add_xp(pet, XP_PER_MESSAGE)
    pet.mood = min(100, pet.mood + 5)

    response, updated_memory = get_pet_response(
        pet_name=pet.name, pet_state=pet.state,
        user_emotion=emotion, user_message=user_message,
        memory=pet.memory or '', level=pet.level
    )
    pet.memory = updated_memory

    # save chat history
    db.session.add(ChatHistory(user_id=session['user_id'], role='user', message=user_message))
    db.session.add(ChatHistory(user_id=session['user_id'], role='pet', message=response))
    db.session.commit()

    xp_progress = (pet.xp % XP_PER_LEVEL) * 100 // XP_PER_LEVEL
    return jsonify({
        'response': response,
        'pet_state': pet.state,
        'xp': pet.xp,
        'level': pet.level,
        'xp_progress': xp_progress,
        'levelled_up': levelled_up
    })

@pet_bp.route('/activity', methods=['POST'])
@login_required
def activity():
    data = request.get_json()
    action = data.get('action')
    pet = Pet.query.filter_by(user_id=session['user_id']).first()
    fsm = PetFSM(initial_state=pet.state)

    activity_triggers = {'feed': 'feed', 'play': 'play', 'rest': 'rest'}
    activity_messages = {
        'feed': 'You fed me!',
        'play': 'You want to play with me!',
        'rest': 'You put me to rest.',
    }
    if action not in activity_triggers:
        return jsonify({'error': 'Unknown action'}), 400

    getattr(fsm, activity_triggers[action])()
    pet.state = fsm.get_state()

    # update stats based on activity
    if action == 'feed':
        pet.hunger = min(100, pet.hunger + 40)
    elif action == 'play':
        pet.mood = min(100, pet.mood + 20)
        pet.energy = max(0, pet.energy - 10)
    elif action == 'rest':
        pet.energy = min(100, pet.energy + 40)

    add_xp(pet, 5)
    response, updated_memory = get_pet_response(
        pet_name=pet.name, pet_state=pet.state,
        user_emotion='happy', user_message=activity_messages[action],
        memory=pet.memory or '', level=pet.level
    )
    pet.memory = updated_memory
    db.session.add(ChatHistory(user_id=session['user_id'], role='pet', message=response))
    db.session.commit()

    xp_progress = (pet.xp % XP_PER_LEVEL) * 100 // XP_PER_LEVEL
    return jsonify({
        'response': response,
        'pet_state': pet.state,
        'hunger': pet.hunger,
        'mood': pet.mood,
        'energy': pet.energy,
        'xp_progress': xp_progress,
        'level': pet.level
    })

@pet_bp.route('/theme', methods=['POST'])
@login_required
def switch_theme():
    data = request.get_json()
    theme = data.get('theme', 'normal')
    user = User.query.get(session['user_id'])
    user.theme = theme
    session['theme'] = theme
    db.session.commit()
    return jsonify({'success': True, 'theme': theme})

@pet_bp.route('/rename', methods=['POST'])
@login_required
def rename():
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False})
    pet = Pet.query.filter_by(user_id=session['user_id']).first()
    pet.name = name
    db.session.commit()
    return jsonify({'success': True, 'name': name})
