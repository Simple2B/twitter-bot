from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class AddTwitterAccountForm(FlaskForm):
    username = StringField('Twitter Account', [DataRequired()])
    submit = SubmitField('Add Account')
