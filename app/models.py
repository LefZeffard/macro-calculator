from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False)
    target_calories: so.Mapped[float] = so.mapped_column(nullable=False)
    target_protein: so.Mapped[float] = so.mapped_column(nullable=False)
    target_fat: so.Mapped[float] = so.mapped_column(nullable=False)
    meals: so.Mapped[list['Meal']] = so.relationship(back_populates='user', order_by='Meal.timestamp')

    def __repr__(self):
        return f"{self.username}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Meal(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True, nullable=False)
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True),
                                                      default=lambda: datetime.now(timezone.utc),
                                                      index=True, 
                                                      nullable=False)
    calories: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
    protein: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
    fat: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
    user: so.Mapped['User'] = so.relationship(back_populates='meals')
    
    def local_time(self, tz_name):
        ts = self.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        try:
            return ts.astimezone(ZoneInfo(tz_name))
        except ZoneInfoNotFoundError:
            return ts.astimezone(ZoneInfo("UTC"))
    



    
