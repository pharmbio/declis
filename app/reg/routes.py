from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.reg.forms import EmptyForm, RodForm, RodCheckForm, LibraryForm, SampleForm, SequencingForm
from app.models import User, Lib, Seq, Sample, Rod
from app.reg import bp

#admin_permission = Permission(RoleNeed('admin'))

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/check', methods=['GET', 'POST'])
def rod_chk():
    from base64 import b64decode
    form = RodCheckForm()
    proj = form.proj.data
    pairs = form.pairs.data
    pairs = eval(pairs)
    pairs = b64decode(pairs)
    pairs = pairs.decode()
    pairs = eval(pairs)
    # pairs = eval(b64decode(eval(form.pairs.data)).decode())
    
   
    if form.validate_on_submit():
        flash('ROD pairs defined for project {}'.format(proj))
        
        # return redirect(url_for('main.index'))
        return render_template('rod_confirm.html', title='Confirm ROD sample pairs', \
            proj=proj, pairs=pairs)
    return render_template('rod_check.html', title='Empty ROD sample pairs', \
        form=form, proj=proj, pairs=pairs)


@bp.route('/pairs', methods=['GET', 'POST'])
def rod_reg():
    from base64 import b64encode
    form = RodForm()
    seqs = Seq.query.all()
    menu = []
    for seq in seqs:
        menu.append((seq.id, "D{:02} {}".format(seq.id, seq.proj)))
    form.proj.choices = [(0,"select a project")] + menu
    if form.validate_on_submit():
        proj = Seq.query.filter_by(id=form.proj.data).first_or_404()
        pairs = rod_serial(proj, form.pairs.data)
        pairs = rod_curr(pairs)
        form.submit.label.text = 'Confirm'
        return render_template('rod_check.html', title='Register sample pairs for ROD', \
            form=form, proj=proj, pairs=pairs, trans=b64encode(str(pairs).encode()))
    return render_template('rod_select.html', 
        title='Register sample pairs for ROD', form=form)
    # flash('ROD pairs defined')

def rod_serial(proj, dat):
    sams = Sample.query.with_entities(Sample.name, Sample.id).filter_by(seq_id=proj.id).all()
    sams = dict(sams)

    a, b, pairs = '', '', []
    dat = dat.splitlines()
    for line in dat:
        line = line.strip()
        if a and b and not line:
            pairs.append((a, b))
            a, b = '', ''
        elif a and line:
            b = (sams.get(line, -1), line)
        elif line:
            a = (sams.get(line, -1), line)
    if a and b: pairs.append((a, b))
    return pairs

def rod_curr(pairs):
    curr = Rod.query.with_entities(Rod.prot).all()
    curr = [x[0] for x in curr]
    junk = []
    for q in pairs:
        if q[0][0] == -1 or q[1][0] == -1:
            junk.append(('reject', *q))
        elif q[0][0] in curr:
            junk.append(('update', *q))
        else:
            junk.append(('new', *q))
    return junk


@bp.route('/libreg', methods=['GET', 'POST'])
def lib_reg():
    form = LibraryForm()
    if form.validate_on_submit():
        # do something here
        return redirect(url_for('index'))
    return render_template('lib_reg.html', title='New Library', form=form)


@bp.route('/samreg', methods=['GET', 'POST'])
def sam_reg():
    form = SampleForm()
    if form.validate_on_submit():
        # do something here
        return redirect(url_for('index'))
    return render_template('sam_reg.html', title='Define Samples', form=form)


@bp.route('/procseq', methods=['GET', 'POST'])
def proc_seq():
    form = SequencingForm()
    if form.validate_on_submit():
        # do something here
        return redirect(url_for('index'))
    return render_template('seq_data.html', title='Process Sequencing Data', form=form)
