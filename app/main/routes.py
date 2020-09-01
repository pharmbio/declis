from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.main.forms import EmptyForm, ChemForm, SearchForm
from app.models import User, Lib, Seq, Sample, Results, Enrich, Chems
from app.main import bp

#admin_permission = Permission(RoleNeed('admin'))

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # seqs = Seq.query.all()
    return render_template('index.html', title='Home')


@bp.route('/sequencing')
@login_required
def results():
    seqs = Seq.query.all()
    return render_template('seqruns.html', title='Results', seqs=seqs)


@bp.route('/chem', methods=['GET', 'POST'])
@login_required
def chem_ask():
    form = ChemForm()
    if form.validate_on_submit():
        bb = "{}_{}_{}".format(form.bb1.data,form.bb2.data,form.bb3.data)
        hit = Chems.query.filter_by(bb=bb).first_or_404()
        return render_template('chem.html', title='Chemical Structure', form=form, hit=hit)
    return render_template('chem.html', title='Chemical Structure', form=form)


@bp.route('/chems', methods=['GET', 'POST'])
@login_required
def find_chems():
    form = ChemForm()
    if form.validate_on_submit():
        crit = {}
        if form.bb1.data != '*':
            crit["b1"] = form.bb1.data
        if form.bb2.data != '*':
            crit["b2"] = form.bb2.data
        if form.bb3.data != '*':
            crit["b3"] = form.bb3.data
        hits = Chems.query.filter_by(**crit).all()
        return render_template('chems.html', title='Chemical Structures', form=form, hits=hits)
    return render_template('chem.html', title='Chemical Structure', form=form)


@bp.route('/search', methods=['GET', 'POST'])
@login_required
def find_hits():
    form = SearchForm()
    samples = Sample.query.all()
    menu = []
    for sam in samples:
        menu.append((sam.id, "D{:02d} {}".format(sam.seq_id, sam.name)))
    form.sample.choices = [(0,"select a sample")] + menu
    form.naive.choices  = [(0,"select a naive (optional)")] + menu
    form.ntc.choices    = [(0,"select an NTC (optional)")] + menu
    if form.validate_on_submit():
        hits = (form.limit.data,form.sample.data,form.naive.data,form.ntc.data)
        return render_template('search.html', title='Find dataset', form=form, hits=hits)
    return render_template('search.html', title='Find dataset', form=form)



@bp.route('/sample/<sam>')
@login_required
def samres(sam):
    sample  = Sample.query.filter_by(id=sam).first_or_404()
    seq     = Seq.query.filter_by(id=sample.seq_id).first_or_404()
    samples = Sample.query.filter_by(seq_id=seq.id).all()

    enrich_top = Enrich.query.filter_by(sample=sam).order_by('rank').limit(20)
    sam_list = [x.id for x in samples]
    sam_pos  = sam_list.index(int(sam))
    sam_next = sam_list[sam_pos+1] if int(sam) < max(sam_list) else 0
    sam_prev = sam_list[sam_pos-1] if int(sam) > min(sam_list) else 0
    form = EmptyForm()
    return render_template('details.html', seq=seq, sample=sample, sam_next=sam_next, sam_prev=sam_prev, enrich_top=enrich_top, form=form)


@bp.route('/seq/<sid>')
@login_required
def seqres(sid):
    seq     = Seq.query.filter_by(id=sid).first_or_404()
    samples = Sample.query.filter_by(seq_id=seq.id).all()
    seqruns = Seq.query.all()

    seq_list = [x.id for x in seqruns]
    seq_pos  = seq_list.index(int(sid))
    seq_next = seq_list[seq_pos+1] if int(sid) < max(seq_list) else 0
    seq_prev = seq_list[seq_pos-1] if int(sid) > min(seq_list) else 0

    form = EmptyForm()
    return render_template('samples.html', seq=seq, samples=samples, seq_next=seq_next, seq_prev=seq_prev, form=form)


@bp.route('/seq/<seq>/all')
@login_required
def seqresall(seq):
    seq = Seq.query.filter_by(id=seq).first_or_404()
    samples = Sample.query.filter_by(seq_id=seq.id).all()
    form = EmptyForm()
    return render_template('showall.html', seq=seq, samples=samples, form=form)


@bp.route('/admin')
#@admin_permission.require()
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Admins only')
        return redirect(url_for('main.index'))
    return render_template('admin.html', title=current_user.role)
