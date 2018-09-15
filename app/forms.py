from flask_wtf import FlaskForm
from wtforms import StringField,BooleanField,SubmitField,PasswordField,RadioField
from wtforms.validators import DataRequired,EqualTo


class LoginForm(FlaskForm):
    username=StringField("identifiant",validators=[DataRequired("Entrer votre nom d'utilisateur")])
    password=PasswordField("Mot de passe", validators=[DataRequired("Entrer votre mot passe")])
    remember_me=BooleanField("Se souvenir de moi")
    submit=SubmitField("Se connecter")

class ProfileForm(FlaskForm):
    username = StringField("identifiant", validators=[DataRequired()])
    password = PasswordField("Nouveau mot de passe", validators=[DataRequired("Entrer un nouveau mot passe"),EqualTo('confirm_password', message='Passwords must match')])
    confirm_password=PasswordField("Confirmer votre nouveau mot de passe", validators=[DataRequired()])
    submit = SubmitField("Sauvegarder vos modifications")

class AccueilForm(FlaskForm):
    nom=StringField("Nom", validators=[DataRequired()])
    pages=RadioField("domaines : ",choices=[("Les pages","pages"),("Les Personnes","personnes")])
    submit=SubmitField("Rechercher")