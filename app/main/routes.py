from app import db
from flask import current_app, render_template, request, jsonify
from app.main import bp
from app.models import Tweet, Test


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    tweets = Tweet.query.all()

    return render_template('index.html', tweets=tweets)


@bp.route('/stories', methods=['GET', 'POST'])
def stories():
    return render_template("stories.html")


@bp.route('/process', methods=['GET', 'POST'])
def process():
    return render_template("process.html")


@bp.route('/process/observe', methods=['GET', 'POST'])
def test():
    project_name = request.form['project_name']

    if project_name:
        tb_test = Test()
        tb_test.name = project_name
        db.session.add(tb_test)
        db.session.commit()

        return jsonify(status_observe="success")
    else:
        return jsonify(status_observe="failed")
