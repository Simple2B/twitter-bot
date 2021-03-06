import os
import enum

from sqlalchemy import Enum

from app import db
from app.models.utils import ModelMixin


class Bot(db.Model, ModelMixin):

    __tablename__ = 'bot'

    class StatusType(enum.Enum):
        active = "active"
        disabled = "disabled"

    class ActionType(enum.Enum):
        start = 'start'
        stop = 'stop'
        restart = 'restart'

    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, default=0)
    status = db.Column(Enum(StatusType), default=StatusType.disabled)
    action = db.Column(Enum(ActionType), default=ActionType.stop)

    @property
    def is_active(self):
        if not self.pid:
            return False
        try:
            os.kill(self.pid, 0)
        except OSError:
            return False
        else:
            return True
