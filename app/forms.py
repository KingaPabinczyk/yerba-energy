from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, TextAreaField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Email, Regexp
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
    username = StringField("Login", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Hasło", validators=[DataRequired(), Length(min=6)])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    first_name = StringField("Imię", validators=[DataRequired(), Length(min=2, max=100)])
    last_name = StringField("Nazwisko", validators=[DataRequired(), Length(min=2, max=100)])
    street = StringField("Ulica", validators=[DataRequired()])
    house_number = StringField("Nr domu/lokalu", validators=[DataRequired()])
    postal_code = StringField("Kod pocztowy", validators=[
        DataRequired(),
        Regexp(r"^\d{2}-\d{3}$", message="Kod pocztowy w formacie 00-000")
    ])
    city = StringField("Miejscowość", validators=[DataRequired()])
    submit = SubmitField("Zarejestruj")
