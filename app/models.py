from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    role = db.Column(db.String(32))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))


    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Lib(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seqs = db.relationship('Seq', backref='layout', lazy='dynamic')


class Seq(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proj = db.Column(db.String(32))
    date = db.Column(db.Date)
    delivery = db.Column(db.String(32))
    status = db.Column(db.String(32))
    folder = db.Column(db.String(128))
    comment = db.Column(db.String(255))
    lib_id = db.Column(db.Integer, db.ForeignKey('lib.id'))
    samples = db.relationship('Sample', backref='run_id', lazy='dynamic')


class Sample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seq_id = db.Column(db.Integer, db.ForeignKey('seq.id'))
    snum = db.Column(db.String(15))
    r = db.Column(db.Integer)
    name = db.Column(db.String(127))
    protein_umol = db.Column(db.Float)
    lib_pmol = db.Column(db.Float)
    bead_type = db.Column(db.String(127))
    bead_ul = db.Column(db.Float)
    washes = db.Column(db.Integer)
    spike = db.Column(db.String(127))
    special = db.Column(db.String(127))
    access = db.Column(db.String(127))
    target = db.Column(db.String(127))



class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sample = db.Column(db.Integer, db.ForeignKey('sample.id'), index=True)
    b1 = db.Column(db.Integer)
    b2 = db.Column(db.Integer)
    b3 = db.Column(db.Integer)
    bb = db.Column(db.String(31))
    copies = db.Column(db.Integer)
    relative = db.Column(db.Float)


class Enrich(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base = db.Column(db.Integer, db.ForeignKey('sample.id'))
    sample = db.Column(db.Integer, db.ForeignKey('sample.id'), index=True)
    b1 = db.Column(db.Integer)
    b2 = db.Column(db.Integer)
    b3 = db.Column(db.Integer)
    enrich = db.Column(db.Float)
    rank = db.Column(db.Integer)


class Chems(db.Model):
    # need to add library
    id = db.Column(db.Integer, primary_key=True)
    lib_id = db.Column(db.Integer, db.ForeignKey('lib.id'))
    b1 = db.Column(db.Integer)
    b2 = db.Column(db.Integer)
    b3 = db.Column(db.Integer)
    bb = db.Column(db.String(31), index=True)
    smi = db.Column(db.String(256))


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lib_id = db.Column(db.Integer, db.ForeignKey('lib.id'))
    b1 = db.Column(db.Integer)
    b2 = db.Column(db.Integer)
    b3 = db.Column(db.Integer)
    smi = db.Column(db.String(256))
    note = db.Column(db.String(256))


class Rod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prot = db.Column(db.Integer, db.ForeignKey('sample.id'))
    sans = db.Column(db.Integer, db.ForeignKey('sample.id'))