from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FloatField,
    SelectField,
)
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
    category = SelectField('Category', coerce=int, render_kw={'class': 'minimal-select'})
    unit = SelectField('Unit', coerce=int, render_kw={'class': 'minimal-select'})
    submit = SubmitField('Save')


class DefaultSettingsForm(FlaskForm):
    language = SelectField(
        'Default language',
        coerce=str,
        render_kw={'class': 'minimal-select'},
    )
    currency = SelectField(
        'Default currency',
        coerce=str,
        render_kw={'class': 'minimal-select'},
    )
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Language, Currency

        self.language.choices = [
            (lang.code, lang.name) for lang in Language.query.all()
        ]
        self.currency.choices = [
            (
                cur.code,
                f"{cur.code} - {cur.name}",
            )
            for cur in Currency.query.all()
        ]


class DeleteForm(FlaskForm):
    """Simple form providing CSRF protection for delete actions."""

    submit = SubmitField('Delete')
