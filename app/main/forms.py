from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Chems


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class ChemForm(FlaskForm):
    bb1 = StringField('BB 1', validators=[DataRequired()])
    bb2 = StringField('BB 2', validators=[DataRequired()])
    bb3 = StringField('BB 3', validators=[DataRequired()])
    submit = SubmitField('Find Chem')


class SearchForm(FlaskForm):
    limit = IntegerField('Limit', validators=[DataRequired()])
    sample = SelectField('Sample', coerce=int)
    naive  = SelectField('Naive', coerce=int)
    ntc    = SelectField('NTC', coerce=int)
    submit = SubmitField('Find Hits')