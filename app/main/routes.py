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
    samples = Sample.query.filter(Sample.seq_id > 5).all()
    menu = []
    for sam in samples:
        menu.append((sam.id, "D{:02d} {}".format(sam.seq_id, sam.name)))
    form.sample.choices = [(0,"select a sample")] + menu
    form.naive.choices  = [(0,"select a naive (optional)")] + menu
    form.ntc.choices    = [(0,"select an NTC (optional)")] + menu
    if form.validate_on_submit():
        if not form.sample.data:
            flash("Ain't gonna see nuthin without pickin a sample.")
            return render_template('search.html', title='Find dataset', form=form)
        elif not form.naive.data and not form.ntc.data:
            # need to specify library size
            hits = resdump(form.limit.data, form.sample.data, 1000)
            return render_template('search.html', title='Find dataset', form=form, hits=hits)
        elif form.ntc.data:
            flash("Comparison to NTC not yet implemented")
            return render_template('search.html', title='Find dataset', form=form)
        elif form.naive.data:
            enrich = enrank(form.limit.data, form.sample.data, form.naive.data)
            return render_template('search.html', title='Find dataset', form=form, enrich=enrich)
    return render_template('search.html', title='Find dataset', form=form)

def resdump(lim, sid, size):
    sample = Results.query.filter_by(sample=sid).order_by(Results.copies.desc()).limit(lim)
    smi = Chems.query.with_entities(Chems.bb,Chems.smi).all()
    smi = dict(smi)
    out = []
    for sam in sample:
        out.append((sam.b1,sam.b2,sam.b3,sam.copies,round(size*sam.relative,4),smi[sam.bb]))
    return out

def enrank(lim, sid, nid):
    sam = Results.query.with_entities(Results.bb,Results.relative).filter_by(sample=sid).all()
    nai = Results.query.with_entities(Results.bb,Results.relative).filter_by(sample=nid).all()
    smi = Chems.query.with_entities(Chems.bb,Chems.smi).all()
    sam = dict(sam)
    nai = dict(nai)
    smi = dict(smi)
    enr = []
    for bb in sam:
        enr.append((bb, round(sam[bb]/nai[bb],4), smi[bb]))
    enr.sort(key=lambda x: x[1], reverse=True)
    return enr[:lim]
    # return (len(sam), len(nai))

def rank_simple(dat):
    return sorted(range(len(dat)), key=dat.__getitem__, reverse=True)

def rankdata(dat):
    n = len(dat)
    ivec = rank_simple(dat)
    svec = [dat[rank] for rank in ivec]
    sumranks = 0
    dupcount = 0
    newarray = [0]*n
    for i in range(n):
        sumranks += i
        dupcount += 1
        if i==n-1 or svec[i] != svec[i+1]:
            averank = sumranks / float(dupcount) + 1
            for j in range(i-dupcount+1,i+1):
                newarray[ivec[j]] = averank
            sumranks = 0
            dupcount = 0
    return newarray


@bp.route('/simple/<sam>')
@login_required
def simres(sam):
    sample  = Sample.query.filter_by(id=sam).first_or_404()
    seq     = Seq.query.filter_by(id=sample.seq_id).first_or_404()
    samples = Sample.query.filter_by(seq_id=seq.id).all()

    # enrich_top = Enrich.query.filter_by(sample=sam).order_by('rank').limit(20)
    # enrich_top = Enrich.query.join(Chems, Enrich.bb == Chems.bb).\
    #    filter(Enrich.sample == sam).order_by('rank').limit(20)
    # enrich_top = Enrich.query.join(Chems, Enrich.bb == Chems.bb).\
    #    filter(Enrich.sample == sam).add_columns(Chems.smi).order_by('rank').limit(20)
    enrich_top = db.session.query(Enrich, Chems).join(Chems, Enrich.bb == Chems.bb).\
        filter(Enrich.sample == sam).order_by('rank').limit(20)

    sam_list = [x.id for x in samples]
    sam_pos  = sam_list.index(int(sam))
    sam_next = sam_list[sam_pos+1] if int(sam) < max(sam_list) else 0
    sam_prev = sam_list[sam_pos-1] if int(sam) > min(sam_list) else 0
    form = EmptyForm()
    return render_template('details2.html', seq=seq, sample=sample, sam_next=sam_next, sam_prev=sam_prev, enrich_top=enrich_top, form=form)

@bp.route('/sample/<sam>')
@login_required
def samres(sam):
    sample  = Sample.query.filter_by(id=sam).first_or_404()
    seq     = Seq.query.filter_by(id=sample.seq_id).first_or_404()
    samples = Sample.query.filter_by(seq_id=seq.id).all()

    # enrich_top = Enrich.query.filter_by(sample=sam).order_by('rank').limit(20)
    # enrich_top = Enrich.query.join(Chems, Enrich.bb == Chems.bb).\
    #    filter(Enrich.sample == sam).order_by('rank').limit(20)
    # enrich_top = Enrich.query.join(Chems, Enrich.bb == Chems.bb).\
    #    filter(Enrich.sample == sam).add_columns(Chems.smi).order_by('rank').limit(20)
    enrich_top = db.session.query(Enrich, Chems).join(Chems, Enrich.bb == Chems.bb).\
        filter(Enrich.sample == sam).order_by('rank').limit(20)

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
