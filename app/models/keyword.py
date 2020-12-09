from app import db
from app.models.utils import ModelMixin


class Keyword(db.Model, ModelMixin):

    __tablename__ = 'keywords'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(60), unique=True, nullable=False)
