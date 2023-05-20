from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectMultipleField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo

from app.models import User


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_login(self, login):
        user = User.get_by_login(login.data)
        if user is not None:
            raise ValidationError('Используйте другое имя')
        return

class AddAdForm(FlaskForm):
    name_object = StringField('Название объекта', validators=[DataRequired()])
    name_city = SelectField('Город', coerce=int)
    name_street = SelectField('Улица', coerce=int)
    name_district = SelectField('Район', coerce=int)
    name_subway = SelectField('Станция метро', coerce=int)
    number = IntegerField('Номер дома', validators=[DataRequired()])
    building = StringField('Строение')
    amount_rooms = IntegerField('Количество комнат', validators=[DataRequired()])
    metr = IntegerField('Метраж', validators=[DataRequired()])
    floorness = IntegerField('Этажность', validators=[DataRequired()])
    floor = IntegerField('Этаж', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    type_of_deal = SelectField('Тип сделки', coerce=int)
    description = TextAreaField('Описание', validators=[DataRequired()])
    photo = FileField('Фото', validators=[DataRequired()])
    submit = SubmitField('Разместить')


class SearchForm(FlaskForm):
    name_object = StringField('Название', validators=[DataRequired()])
    amount_rooms = IntegerField('Количество комнат', validators=[DataRequired()])
    price = IntegerField('Максимальная цена', validators=[DataRequired()])
    type_of_deal = SelectField('Тип сделки', coerce=int)
    submit = SubmitField('Поиск')
