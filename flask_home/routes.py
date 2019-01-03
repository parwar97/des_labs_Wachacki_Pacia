"""
Plik zawierajacy glowne funkcje widoku.
"""

from flask_home import app, db, bcrypt, mail, devices, humi_temp_data
from flask import render_template, flash, redirect, url_for, request
from flask_home.models import User
from flask_home.forms import (
    LoginForm,
    RegistrationForm,
    RequestResetForm,
    ResetPasswordForm,
    UpdateAccountForm)
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import RPi.GPIO as GPIO


# Strona rejestracji nowego uzytkownika.
@app.route('/register', methods=['GET','POST'])
@login_required
def register():
    form = RegistrationForm()
    # Jezeli uzytkownik poprawnie wypelnil formularz to zapisujemy go w bazie danych.
    if form.validate_on_submit():
        # Dodanie uzytkownika do bazy dnaych.
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# Strona logowania uzytkownika do aplikacji.
@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET','POST'])
def login():
    # Uzytkownikow zalogowanych przekierowywujemy na strone domowa.
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    # Sprawdzamy czy uzytkownik podal poprawne dane.
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
	# Jezeli istnieje w bazie danych uzytkownik i podal on poprawne haslo to tworymy dla niego sesje.
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You are logged in.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password!', 'danger')
    return render_template('login.html', form=form)


# Wylogowanie uzytkownika.
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are log out.', 'success')
    return redirect(url_for("login"))


def send_reset_email(user):
    """
    Funkcja Wysylajaca mail do uzytkownika z linkiem do zmiany hasla.

    :param user: Obiekt uzytkownika
    :return: None
    """

    # Utworzenie tokenu.
    token = user.get_reset_token()
    # Utworzenie wiadomosci.
    msg = Message('Password Reset Request', sender='pibermaw@gmail.com', recipients=[user.email])
    msg.body = "To reset your password, visit the following link: %s \
                If you did not make this request then simply ignore this \
                email and no changes will be made. " % ( url_for('reset_token', token=token, _external=True) )
    # Wyslanie wiadomosci.
    mail.send(msg)


# Strona pobrania maila do zmiany hasla.
@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    form = RequestResetForm()
    if form.validate_on_submit():
        # Jezeli istnieje mail w bazie danych to wysylamy link do resetowania hasla.
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('login'))
        else:
            flash("An email doesn't exist in database.", "info")
            return redirect(url_for('reset_password'))
    return render_template('reset_password.html', form=form)


# Strona do zresetowania hasla.
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    # Jesli token jest niewazny to odsylamy uzytkownika do strony pobierania maila.
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Jezeli token jest wazny to pobieramy i resetujemy haslo.
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', form=form)


# Strona danych uzytkownika.
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # Jezeli uzytkownik wprowadzil nowe dane to wpisujemy je do baz danych.
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("account.html", form=form)


# Strona glowna aplikacji - centrum kontroli.
@app.route('/home')
@login_required
def home():
    # Pobranie danych z czujnikow.
    info = {'temp': humi_temp_data[1], 'humi': humi_temp_data[0]}
    return render_template("home.html", devices=devices, info=info)


# Strona kontroli urzadzen - nie generuje widoku.
@app.route('/device/<name>/<state>')
@login_required
def control(name, state):
    # Jezeli przyszedl rozkaz z wlaczneiem urzadzenia 
    # to je wlaczamy (ON), jesli nie to wylaczamy (OFF).
    if state == 'on':
        # Wlaczenie urzadzenia.
        devices[name]['state'] = GPIO.LOW
        GPIO.output(devices[name]['pin'], GPIO.LOW)
    else:
        # Wylaczenie urzadzenia.
        devices[name]['state'] = GPIO.HIGH
        GPIO.output(devices[name]['pin'], GPIO.HIGH)
    # Przekierowanie do konkretnego fragmentu strony.
    return redirect(url_for('home') + '#' + name)
