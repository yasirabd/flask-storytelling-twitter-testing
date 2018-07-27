from app import db
from flask import current_app, render_template, request, jsonify
import os
from app.main import bp
from app.models import Tweet, Test, Preprocess
from ..modules.preprocess import Normalize, Tokenize, SymSpell


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


@bp.route('/process/preprocess', methods=['GET', 'POST'])
def preprocess():
    tweets = Tweet.query.all()
    # separate text into list
    list_tweets = []
    for t in tweets:
        id_tweet = [t.id, t.text]
        list_tweets.append(id_tweet)

    # define
    normalizer = Normalize()
    tokenizer = Tokenize()
    symspell = SymSpell(max_dictionary_edit_distance=3)
    SITE_ROOT = os.path.abspath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "..\data", "corpus_complete_model.json")
    symspell.load_complete_model_from_json(json_url, encoding="ISO-8859-1")

    # do preprocess
    result = []
    for tweet in list_tweets:
        id, text = tweet[0], tweet[1]

        # normalize
        tweet_norm = normalizer.remove_ascii_unicode(text)
        tweet_norm = normalizer.remove_rt_fav(tweet_norm)
        tweet_norm = normalizer.lower_text(tweet_norm)
        tweet_norm = normalizer.remove_newline(tweet_norm)
        tweet_norm = normalizer.remove_url(tweet_norm)
        tweet_norm = normalizer.remove_emoticon(tweet_norm)
        tweet_norm = normalizer.remove_hashtag_mention(tweet_norm)
        tweet_norm = normalizer.remove_punctuation(tweet_norm)

        # tokenize
        tweet_tok = tokenizer.WordTokenize(tweet_norm, removepunct=True)

        # spell correction
        temp = []
        for token in tweet_tok:
            suggestion = symspell.lookup(phrase=token, verbosity=1, max_edit_distance=3)

            # option if there is no suggestion
            if len(suggestion) > 0:
                get_suggestion = str(suggestion[0]).split(':')[0]
                temp.append(get_suggestion)
            else:
                temp.append(token)
        tweet_prepared = ' '.join(temp)

        id_tweet_prepared = [id, tweet_prepared]
        result.append(id_tweet_prepared)

    # insert into table preprocess
    for res in result:
        id, text = res[0], res[1]

        tb_preprocess = Preprocess()
        tb_preprocess.text = text
        tb_preprocess.tweet_id = id
        db.session.add(tb_preprocess)
        db.session.commit()

    return jsonify(status_preprocessing="success")
