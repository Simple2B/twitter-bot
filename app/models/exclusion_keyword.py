from app import db
from app.models.utils import ModelMixin


class ExclusionKeyword(db.Model, ModelMixin):

    __tablename__ = 'exclusion_keywords'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(60), unique=True, nullable=False)
