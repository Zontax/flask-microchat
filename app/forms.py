from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class RegistrationForm(FlaskForm):
    nickname = StringField("Нікнейм", validators=[DataRequired(), Length(min=3, max=24)])
    username = StringField("Логін", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password2 = PasswordField("Повторіть пароль", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Зареєструватись")

    def validate_username(self, username):  # Перевірка логіна
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Цей логін зайнято")

    def validate_email(self, email):  # Перевірка пошти
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Ця адреса зайнята")


class LoginForm(FlaskForm):
    '''Класс форми входу в аккаунт'''
    username = StringField("Логін", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запам'ятати мене")
    submit = SubmitField("Увійти")


class EditProfileForm(FlaskForm):
    nickname = StringField("Нік", validators=[DataRequired(), Length(min=3, max=24)])
    username = StringField("Логін", validators=[DataRequired()])
    about_me = TextAreaField("Про себе", validators=[Length(min=0, max=140)])
    submit = SubmitField("Зберегти")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Цей логін зайнято!")


class PostForm(FlaskForm):
    post = TextAreaField("", validators=[DataRequired(), Length(min=2, max=300)])
    submit = SubmitField("Надіслати")



class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Запит на скидання пароля")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Пароль", validators=[DataRequired()])
    password2 = PasswordField(
        "Повторіть пароль", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Запит на скидання пароля")
