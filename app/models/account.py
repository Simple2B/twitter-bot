import enum

from sqlalchemy import Enum

from app import db
from app.models.utils import ModelMixin


class Account(db.Model, ModelMixin):

    __tablename__ = 'accounts'

    class RoleType(enum.Enum):
        news = 'news'
        exclusion = 'exclusion'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    role = db.Column(Enum(RoleType))
    consumer_key = db.Column(db.String(256), nullable=False)
    consumer_secret = db.Column(db.String(256), nullable=False)
    access_token = db.Column(db.String(256), nullable=False)
    access_token_secret = db.Column(db.String(256), nullable=False)
