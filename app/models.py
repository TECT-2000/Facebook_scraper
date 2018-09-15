from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from app import login,db
from scrapy.item import Item,Field
from json import JSONEncoder
from app import app

class User(UserMixin):

    def __init__(self):
        self.id = 1234
        self.username=app.config["USERNAME"]
        self.set_password(app.config["MOT_DE_PASSE"])

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return int(self.id)

    @login.user_loader
    def load_user(user_id):
        u = User()
        if u.get_id() == user_id:
            return u
        else:
            return None

