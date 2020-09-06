from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.reg.forms import EmptyForm, LibraryForm, SampleForm, SequencingForm, RodForm
from app.models import User, Lib, Seq, Sample
from app.reg import bp

#admin_permission = Permission(RoleNeed('admin'))

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/rod_check', methods=['GET', 'POST'])
def rod_chk(proj, pairs):
    form = EmptyForm()
    proj = Seq.query.filter_by(id=proj).first_or_404()
    curr = Rod.query.all()
    sams = Sample.query.filter_by(seq_id=proj.id).all()
    if form.validate_on_submit():
        flash('ROD pairs defined')
        return redirect(url_for('main.index'))
    return render_template('rod_check.html', title='Confirm sample pairs for ROD', \
        form=form, proj=proj, pairs=pairs, curr=curr, sams=sams)


@bp.route('/pairs', methods=['GET', 'POST'])
def rod_reg():
    form = RodForm()
    seqs = Seq.query.all()
    menu = []
    for seq in seqs:
        menu.append((seq.id, "D{:02} {}".format(seq.id, seq.proj)))
    form.proj.choices = [(0,"select a project")] + menu
    if form.validate_on_submit():
        proj = Seq.query.filter_by(id=form.proj.data).first_or_404()
        pairs = []
        a, b = '',''
        for line in form.vics.data:
            line = line.strip()
            if a and b and not line:
                pairs.append((a, b))
                a, b = '', ''
            elif a and line:
                b = line
            elif line:
                a = line
        if a and b: pairs.append((a, b))
        # return redirect(url_for('reg.pairs_check', proj=proj, pairs=pairs))
        return render_template('rod_check.html', \
             title='Register sample pairs for ROD', form=form, proj=proj, pairs=pairs)
    return render_template('rod_select.html', 
        title='Register sample pairs for ROD', form=form)
    # flash('ROD pairs defined')


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
