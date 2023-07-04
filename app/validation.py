from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, EmailField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[validators.DataRequired()])
    password = PasswordField('Şifre', validators=[validators.DataRequired()])
    submit = SubmitField('Giriş Yap')

class RegisterForm(FlaskForm):
    first_name = StringField("İsim",validators=[DataRequired()])
    last_name = StringField("Soyisim",validators=[DataRequired()])
    username = StringField("Kullanıcı Adı",validators=[DataRequired()])
    email = EmailField("Email Adresi",validators=[DataRequired(), validators.Email()])
    address = StringField("Adres",validators=[DataRequired()])
    city = StringField("Şehir",validators=[DataRequired()])
    country = StringField("Ülke",validators=[DataRequired()])
    phone = StringField("Telefon",validators=[DataRequired()])
    password = PasswordField("Parola:",validators=[
        DataRequired(),
        validators.EqualTo(fieldname = "confirm",message="Parolanız Uyuşmuyor...")
    ])
    confirm = PasswordField("Parola Doğrula")
    submit = SubmitField('Kayıt Ol')


