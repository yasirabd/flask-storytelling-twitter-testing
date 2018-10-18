from app import db
from flask import current_app, render_template, request, jsonify
import os
from collections import defaultdict
from app.main import bp
from app.models import Tweet, Test, Preprocess, PosTag, PenentuanKelas, LdaPWZ, GrammarStory
from ..modules.preprocess import Normalize, Tokenize, SymSpell
from ..modules.hmmtagger import MainTagger, Tokenization
from ..modules.lda import LdaModel
from ..modules.grammar import CFG


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    tweets = Tweet.query.all()

    return render_template('index.html', tweets=tweets)


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

        # join attraction with strip
        tweet_prepared = normalizer.join_attraction(tweet_prepared)

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


@bp.route('/process/pos_tagging', methods=['GET', 'POST'])
def pos_tagging():
    tweets_preprocessed = Preprocess.query.all()

    # get text from table Preprocess
    list_tweets = []
    for t in tweets_preprocessed:
        tid_tweet = [t.tweet_id, t.text]
        list_tweets.append(tid_tweet)

    # path
    SITE_ROOT = os.path.abspath(os.path.dirname(__file__))
    lexicon_url = os.path.join(SITE_ROOT, "..\data", "Lexicon.trn")
    ngram_url = os.path.join(SITE_ROOT, "..\data", "Ngram.trn")

    # initialize
    tagger = MainTagger(lexicon_url, ngram_url, 0, 3, 3, 0, 0, False, 0.2, 0, 500.0, 1)
    tokenize = Tokenization()

    # do pos tagging
    result = []
    for tweet in list_tweets:
        tweet_id, text = tweet[0], tweet[1]

        if len(text) == 0:
            tid_text = [tweet_id, text]
            result.append(tid_text)
        else:
            out = tokenize.sentence_extraction(tokenize.cleaning(text))
            join_word = []
            for o in out:
                strtag = " ".join(tokenize.tokenisasi_kalimat(o)).strip()
                join_word += [" ".join(tagger.taggingStr(strtag))]
            tid_text = [tweet_id, join_word]
            result.append(tid_text)

    # insert into table preprocess
    for tweet in result:
        tweet_id, text = tweet[0], tweet[1]
        tweet_str = ''.join(text)

        tb_postag = PosTag()
        tb_postag.text = tweet_str
        tb_postag.tweet_id = tweet_id
        db.session.add(tb_postag)
        db.session.commit()

    return jsonify(status_pos_tagging="success")


@bp.route('/process/penentuan_kelas', methods=['GET', 'POST'])
def penentuan_kelas():
    Ccon = ['JJ', 'NN','NNP', 'NNG', 'VBI', 'VBT']
    Cfunc = ['OP', 'CP', 'GM', ';', ':', '"', '.',
             ',', '-', '...', 'RB', 'IN', 'MD', 'CC',
             'SC', 'DT', 'UH', 'CDO', 'CDC', 'CDP', 'CDI',
             'PRP', 'WP', 'PRN', 'PRL', 'NEG', 'SYM', 'RP', 'FW']

    tweets_tagged = PosTag.query.all()

    # get text from table PostTag
    list_tweets = []
    for t in tweets_tagged:
        tid_tweet = [t.tweet_id, t.text]
        list_tweets.append(tid_tweet)

    # do penentuan kelas
    result = []
    for tweet in list_tweets:
        tweet_id, text = tweet[0], tweet[1]

        if len(text) > 0:
            text_split = text.split(' ')

            doc_complete = {"con": [], "func": []}
            con = []
            func = []

            for word in text_split:
                w = word.split('/', 1)[0]
                tag = word.split('/', 1)[1]
                if tag in Ccon:
                    con.append(word)
                elif tag in Cfunc:
                    func.append(word)
            doc_complete["con"].append(' '.join(con))
            doc_complete["func"].append(' '.join(func))
        else:
            doc_complete["con"].append(text)
            doc_complete["func"].append(text)

        result.append([tweet_id, doc_complete])

    # insert into table penentuan kelas
    for tweet in result:
        tweet_id, text = tweet[0], tweet[1]
        content, function = ''.join(text["con"]), ''.join(text["func"])

        tb_penentuan_kelas = PenentuanKelas()
        tb_penentuan_kelas.content = content
        tb_penentuan_kelas.function = function
        tb_penentuan_kelas.tweet_id = tweet_id
        db.session.add(tb_penentuan_kelas)
        db.session.commit()

    return jsonify(status_penentuan_kelas="success")


@bp.route('/process/lda', methods=['GET', 'POST'])
def lda():
    latest_test_id = (Test.query.order_by(Test.id.desc()).first()).id
    tweets_penentuan_kelas = PenentuanKelas.query.all()

    # get tweets content
    tweets_content_tagged = []
    for tweet in tweets_penentuan_kelas:
        tweets_content_tagged.append(tweet.content)

    # separate word and tag
    documents = []
    for tweet in tweets_content_tagged:
        tweet_split = tweet.split(' ')
        temp = []
        for word in tweet_split:
            w = word.split("/", 1)[0]
            temp.append(w)
        documents.append(temp)

    num_topics = request.form['num_topics']
    alpha = request.form['alpha']
    beta = request.form['beta']
    iterations = request.form['iterations']

    if num_topics and alpha and beta and iterations:
        lda = LdaModel(documents, int(num_topics), float(alpha), float(beta), int(iterations))
        result = lda.get_topic_word_pwz(tweets_content_tagged)

        # insert into table ldapwz
        for r in result:
            topic, word, pwz = r[0], r[1], r[2]

            tb_ldapwz = LdaPWZ()
            tb_ldapwz.topic = topic
            tb_ldapwz.word = word
            tb_ldapwz.pwz = pwz
            tb_ldapwz.test_id = latest_test_id
            db.session.add(tb_ldapwz)
            db.session.commit()

        return jsonify(status_lda="success")
    else:
        return jsonify(status_lda="failed")


@bp.route('/process/grammar', methods=['GET', 'POST'])
def grammar():
    latest_test_id = (Test.query.order_by(Test.id.desc()).first()).id
    ldapwz = LdaPWZ.query.filter_by(test_id=latest_test_id)

    # get topic with words in dictionary
    dict_ldapwz = defaultdict(list)
    for data in ldapwz:
        dict_ldapwz[data.topic].append([data.word, data.pwz])

    # initialize
    cfg = CFG()

    # create sentence for story
    dict_story = cfg.create_sentences_from_data(dict(dict_ldapwz))

    # insert into table GrammarStory
    for topic, list_sentence in dict_story.items():
        for sentence in list_sentence:
            tb_grammar_story = GrammarStory()
            tb_grammar_story.topic = topic
            tb_grammar_story.sentence = sentence
            tb_grammar_story.test_id = latest_test_id
            db.session.add(tb_grammar_story)
            db.session.commit()

    return jsonify(status_grammar="success")


@bp.route('/stories', methods=['GET', 'POST'])
def stories():
    test = Test.query.order_by(Test.id.desc()).all()
    return render_template("stories.html", test=test)


@bp.route('/stories/<int:id>', methods=['GET', 'POST'])
def story(id):
    grammar_story = GrammarStory.query.filter_by(test_id=id)

    # store data in dictionary
    dict_story = defaultdict(list)
    for data in grammar_story:
        dict_story[data.topic].append(data.sentence)

    # topic
    topic = list(dict_story.keys())

    return render_template("story.html", test_id=id, topic=topic)


@bp.route('/stories/<int:id>/get_story', methods=['GET', 'POST'])
def get_story(id):
    jsonData = request.get_json()
    selected_topic = jsonData['selected_topic']
    grammar_story = GrammarStory.query.filter_by(test_id=id, topic=selected_topic)

    result = []
    for data in grammar_story:
        result.append(data.sentence)

    return jsonify(grammar_story='. '.join(i.capitalize() for i in result))


@bp.route('/stories/<int:id>/details/data', methods=['GET', 'POST'])
def get_data(id):
    tweets = Tweet.query.all()

    return render_template("details_data.html", test_id=id, tweets=tweets)


@bp.route('/stories/<int:id>/details/preprocessing', methods=['GET', 'POST'])
def get_preprocessing(id):
    preprocess = Preprocess.query.all()

    return render_template("details_preprocessing.html", test_id=id, preprocess=preprocess)


@bp.route('/stories/<int:id>/details/postag', methods=['GET', 'POST'])
def get_postag(id):
    postag = PosTag.query.all()

    return render_template("details_postag.html", test_id=id, postag=postag)


@bp.route('/stories/<int:id>/details/kelas', methods=['GET', 'POST'])
def get_kelas(id):
    kelas = PenentuanKelas.query.all()

    return render_template("details_kelas.html", test_id=id, kelas=kelas)


@bp.route('/stories/<int:id>/details/lda', methods=['GET', 'POST'])
def get_lda(id):
    lda = LdaPWZ.query.filter_by(test_id=id)

    return render_template("details_lda.html", test_id=id, lda=lda)


@bp.route('/stories/<int:id>/details/story', methods=['GET', 'POST'])
def get_grammar_story(id):
    story = GrammarStory.query.filter_by(test_id=id)

    return render_template("details_story.html", test_id=id, story=story)
