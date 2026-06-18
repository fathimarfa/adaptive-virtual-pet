from flask import Blueprint
pet_bp = Blueprint('pet', __name__)
from app.pet import routes
