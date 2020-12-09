import enum

from sqlalchemy import Enum

from app import db
from app.models.utils import ModelMixin


class Bot(db.Model, ModelMixin):

    __tablename__ = 'bot'

    class StatusType(enum.Enum):
        active = "active"
        disabled = "disabled"

    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, default=0)
    status = db.Column(Enum(StatusType))
