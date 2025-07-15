from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class UnitForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    abbreviation = StringField('Abbreviation', validators=[DataRequired()])
    submit = SubmitField('Save')


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')


class ServiceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    category = SelectField('Category', coerce=int)
    unit = SelectField('Unit', coerce=int)
    submit = SubmitField('Save')




class DefaultSettingsForm(FlaskForm):
    language = SelectField('Default language', coerce=int)
    currency = SelectField('Default currency', coerce=int)
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Language, Currency

        self.language.choices = [
            (lang.id, lang.name) for lang in Language.query.all()
        ]
        self.currency.choices = [
            (cur.id, f"{cur.code} - {cur.name}") for cur in Currency.query.all()
        ]
