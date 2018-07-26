from app import db
from flask import current_app, render_template
from app.main import bp
from app.models import Tweet


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    tweets = Tweet.query.all()

    return render_template('index.html', tweets=tweets)


@bp.route('/stories', methods=['GET', 'POST'])
def stories():
    return render_template("stories.html")
