from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class AddBotAccountForm(FlaskForm):
    name = StringField("Account Name", [DataRequired()])
    role = SelectField(
        "Account role",
        [DataRequired()],
        choices=[("news", "News Account"), ("exclusion", "Exclusion Account")],
    )
    consumer_key = StringField("Consumer Key", [DataRequired()])
    consumer_secret = StringField("Consumer Secret", [DataRequired()])
    account_token = StringField("Account Token", [DataRequired()])
    account_token_secret = StringField("Account Token Secret", [DataRequired()])
    submit = SubmitField("Add Account")
