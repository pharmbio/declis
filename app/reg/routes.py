from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.reg.forms import LibraryForm, SampleForm, SequencingForm
from app.models import User, Lib, Seq, Sample
from app.reg import bp

#admin_permission = Permission(RoleNeed('admin'))

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


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
