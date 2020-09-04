from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Rod


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class RodForm(FlaskForm):
    projects = SelectField('Project', coerce=int)
    vics = TextAreaField('ROD Pairs', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SequencingForm(FlaskForm):
    project = StringField('Project', validators=[DataRequired()])
    delivery = StringField('Delivery', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    loc = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Process Sequencing Data')


class LibraryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    size = StringField('Size', validators=[DataRequired()])
    codon = StringField('Lib Codon', validators=[DataRequired()])
    layout = StringField('Layout', validators=[DataRequired()])
    submit = SubmitField('New Library')


class SampleForm(FlaskForm):
    seqrun = StringField('Experiment', validators=[DataRequired()])
    size = StringField('Size', validators=[DataRequired()])
    codon = StringField('Lib Codon', validators=[DataRequired()])
    layout = StringField('Layout', validators=[DataRequired()])
    submit = SubmitField('Define Samples')
