from app import db


class Tweet(db.Model):
    __tablename__ = 'tweet'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    username = db.Column(db.String(50))
    created = db.Column(db.DateTime)
    text = db.Column(db.String(200))
    latitude = db.Column(db.Text)
    longitude = db.Column(db.Text)
    preprocess = db.relationship('Preprocess', backref='tweet', uselist=False)
    postag = db.relationship('PosTag', backref='tweet', uselist=False)
    penentuan_kelas = db.relationship('PenentuanKelas', backref='tweet', uselist=False)

    def __repr__(self):
        return '<Tweet {}>'.format(self.username)


class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    ldapwz = db.relationship('LdaPWZ', backref='test', lazy='dynamic')
    grammar_story = db.relationship('GrammarStory', backref='test', lazy='dynamic')

    def __repr__(self):
        return '<Test {}>'.format(self.name)


class Preprocess(db.Model):
    __tablename__ = 'preprocess'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=False)

    def __repr__(self):
        return '<Preprocess {}>'.format(self.text)


class PosTag(db.Model):
    __tablename__ = 'postag'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=False)

    def __repr__(self):
        return '<PosTag {}>'.format(self.text)


class PenentuanKelas(db.Model):
    __tablename__ = 'penentuan_kelas'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200))
    function = db.Column(db.String(200))
    tweet_id = db.Column(db.Integer, db.ForeignKey('tweet.id'), nullable=False)

    def __repr__(self):
        return '<PenentuanKelas {} {}>'.format(self.content, self.function)


class LdaPWZ(db.Model):
    __tablename__ = 'ldapwz'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(200))
    topic = db.Column(db.Integer)
    pwz = db.Column(db.String(200))
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)

    def __repr__(self):
        return '<LdaPWZ {} {} {}>'.format(self.word, self.topic, self.pwz)


class GrammarStory(db.Model):
    __tablename__ = 'grammar_story'
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.Integer)
    sentence = db.Column(db.String(1000))
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)

    def __repr__(self):
        return '<GrammarStory {} {}>'.format(self.topic, self.sentence)
