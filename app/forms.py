from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, TextAreaField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed

class ProductForm(FlaskForm):
    name = StringField("Nazwa produktu", validators=[DataRequired()])
    price = FloatField("Cena", validators=[DataRequired()])
    image = FileField("Zdjęcie", validators=[FileAllowed(['jpg','png','jpeg'], "Tylko obrazy!")])
    category = SelectField("Kategoria", choices=[
        ("Yerba klasyczna", "🌿 Klasyczna"),
        ("Energia i pobudzenie", "⚡ Energia"),
        ("Wspomaganie odchudzania", "⚖️ Odchudzanie"),
        ("Odporność", "🛡️ Odporność"),
        ("Relax", "🌙 Relax"),
        ("Yerba owocowa", "🍓 Owocowa"),
        ("Yerba z herbatą", "🍵 Z herbatą")
    ], validators=[DataRequired()])
    description = TextAreaField("Opis")
    properties = TextAreaField("Właściwości / składniki")
    preparation = TextAreaField("Sposób przygotowania")
    submit = SubmitField("Dodaj produkt")


class LoginForm(FlaskForm):
    username = StringField("Login", validators=[DataRequired(), Length(min=3)])
    password = PasswordField("Hasło", validators=[DataRequired()])
    submit = SubmitField("Zaloguj")

class RegisterForm(FlaskForm):
    username = StringField("Login", validators=[DataRequired(), Length(min=3)])
    password = PasswordField("Hasło", validators=[DataRequired()])
    submit = SubmitField("Zarejestruj")
