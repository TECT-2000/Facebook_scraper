import os
basedir=os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    TESTING=True
    UPLOAD_FOLDER="./fichiers/"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EMAIL = "rantanplan@gmail.com"
    MDP = "ronaldo"
    USERNAME="Epiphane"
    MOT_DE_PASSE="1234"
