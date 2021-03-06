from typing import List
from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    activated = db.Column(db.Boolean, default=False)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        user = cls.query.filter_by(username=username).first()
        return user

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        user = cls.query.filter_by(id=_id).first()
        return user

    @classmethod
    def find_all(cls) -> List["UserModel"]:
        return cls.query.all()
