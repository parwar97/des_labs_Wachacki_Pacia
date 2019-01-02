from flask_home import app, db, bcrypt, mail, devices, temp, humi
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
#import flask_home.extensions.dht11 as dht11


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
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='pibermaw@gmail.com', recipients=[user.email])
    msg.body = """To reset your password, visit the following link: %s
                If you did not make this request then simply ignore this
                email and no changes will be made.
                """ % ( url_for('reset_token', token=token, _external=True) )
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', form=form)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("account.html", form=form)



@app.route('/home')
def home():
    '''dht = dht11.DHT11(pin = 14)
    result = dht.read()
    import sys
    if result.is_valid():
        print("Temperature: %d C" % result.temperature,  file=sys.stderr)
        print("Humidity: %d %%" % result.humidity,  file=sys.stderr)
    else:
        print("Error: %d" % result.error_code,  file=sys.stderr)
    temp = result.temperature
    humi = result.humidity'''
    info = {'temp': temp, 'humi':humi}
    return render_template("home.html", devices=devices, info=info)


@app.route('/device/<name>/<state>')
def control(name, state):
    if state == 'on':
        devices[name]['state'] = GPIO.LOW
        GPIO.output(devices[name]['pin'], GPIO.LOW)
    else:
        devices[name]['state'] = GPIO.HIGH
        GPIO.output(devices[name]['pin'], GPIO.HIGH)
    return redirect(url_for('home') + '#' + name)
