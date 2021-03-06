from app import db
from app.models.utils import ModelMixin


class TwitterAccount(db.Model, ModelMixin):

    __tablename__ = 'twitter_accounts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    twitter_id = db.Column(db.Integer(), unique=True)
