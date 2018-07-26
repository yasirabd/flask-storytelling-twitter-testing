from app import db
from flask import current_app, render_template
from app.main import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@bp.route('/stories', methods=['GET', 'POST'])
def stories():
    return render_template("stories.html")
