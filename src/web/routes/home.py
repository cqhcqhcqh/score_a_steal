from flask import Blueprint, render_template
from src.web.tasks import get_all_tasks

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return render_template('index.html', tasks=get_all_tasks())