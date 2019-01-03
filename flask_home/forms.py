"""
Plik z formularzami.
"""

import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flask_home.models import User


class RegistrationForm(FlaskForm):
    """
    Formularz rejestracji nowego uzytkownika.
    """

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=6, max=20)])
    submit = SubmitField('Sign In')

    def validate_username(self, username):
        """
        Metoda sprawdzajaca czy wybrana nazwa uzytkownika nie znajduje sie juz w bazie danych.

        :param username: Nazwa uzytkownika
        :return: None
        """

        user = User.query.filter_by(username=username.data).first()
        if user:
            # Jesli nazwa uzytkownika jest zajeta, rzucamy wyjatek.
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """
        Metoda sprawdzajaca czy wybrany mail uzytkownika nie znajduje sie juz w bazie danych.

        :param email: Email uzytkownika
        :return: None
        """

        user = User.query.filter_by(email=email.data).first()
        if user:
            # Jesli email uzytkownika jest zajety, zwracamy wyjatek.
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_password(self, password):
        """
        Metoda sprawdzajaca czy wybrane haslo zawiera przynajmniej jedna litere i cyfre.

        :param password: Haslo uzytkownika
        :return: None
        """

        message = 'The password must contain at least one number and a letter.'

        # Jesli haslo jest nieprawidlowe rzucamy wyjatek.
        input_password = password.data
        if re.search('[0-9]',input_password) is None:
            raise ValidationError(message)
        elif re.search('[a-zA-z]',input_password) is None:
            raise ValidationError(message)


class LoginForm(FlaskForm):
    """
    Formularz logowania uzytkownika.
    """

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class RequestResetForm(FlaskForm):
    """
    Formularz pobrania maila uzytkownika do resetowania hasla.
    """

    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send mail')

    def validate_email(self, email):
        """
        Metoda sprawdzajaca czy wybrany mail uzytkownika  znajduje sie juz w bazie danych.

        :param email: Email uzytkownika
        :return: None
        """

        user = User.query.filter_by(email=email.data).first()
        if user is None:
            # Jezli nie znaleziono maila to rzucamy wyjatek.
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    """
    Formularz  resetowania hasla.
    """

    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

    def validate_password(self, password):
        """
        Metoda sprawdzajaca czy haslo zawiera przynajmniej jedna litere lub cyfre.

        :param password: Email uzytkownika
        :return: None
        """

        message = 'The password must contain at least one number and a letter.'

        # Jezeli haslo jest niepoprawne to rzucamy wyjatek.
        input_password = password.data
        if re.search('[0-9]',input_password) is None:
            raise ValidationError(message)
        elif re.search('[a-zA-z]',input_password) is None:
            raise ValidationError(message)


class UpdateAccountForm(FlaskForm):
    """
    Formularz  aktualizacji danych uzytkownika.
    """

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        """
        Metoda sprawdzajaca czy wybrana, nowa nazwa uzytkownika nie jest juz zajeta w bazie danych.

        :param username: Nazwa uzytkownika
        :return: None
        """

        if username.data != current_user.username:
            # Jesli nazwa jest zajeta to rzucamy wyjatek.
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """
        Metoda sprawdzajaca czy wybrany  mail uzytkownika nie jest juz zajety w bazie danych.

        :param email: Email uzytkownika
        :return: None
        """

        if email.data != current_user.email:
            # Jesli email jest zajety to rzucamy wyjatek.
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

