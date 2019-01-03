"""
Plik tworzacy i konfigurujacy cala aplikacje.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import RPi.GPIO as GPIO
import threading
import Adafruit_DHT

# Urzadzenia do starowania.
devices = {
    'lamp':{'id':1, 'pin':26, 'state':GPIO.HIGH},
    'electricity':{'id':2, 'pin':19, 'state':GPIO.HIGH},
    'door':{'id':3, 'pin':23, 'state':GPIO.HIGH},
    'heater':{'id':3, 'pin':13, 'state':GPIO.HIGH},
}

# Dane odczytane z czujnika temperatury i wilgotnosci.
humi_temp_data = [0, 0]


def config_app(app):
    """
    Funkcja konfigurujaca aplikacje Flask i jej rozszerzenia

    :return: None
    """
    # Konfiguracja baz danych.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/html/firstapp/flask_home/site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Klucz aplikacji.
    app.config['SECRET_KEY'] = '9da539cebcb6ab591de53483af7b0cf8'
    # Konfiguracja automatycznego wysylania maili.
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = "pibermaw@gmail.com"
    app.config['MAIL_PASSWORD'] = "serwermaras22."


class TempThread(threading.Thread):
    """
    Klasa watku termometru i czujnika wilgotnosci.
    """

    def __init__(self, pin_GPIO):
        threading.Thread.__init__(self)
        # Pin czujnika.
        self.pin = pin_GPIO

    def run(self):
        """
        Kod wykonywany w nowym watku.
        """
        while True:
           # Odczyt czujnika.
           humi, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, self.pin)
           if humi is not None and temp is not None:
               humi_temp_data[0], humi_temp_data[1] = humi, temp


# Utworzenie aplikacji.
#app = Flask(__name__)

# Konfiguracja wyjsc/wejsc GPIO.
GPIO.setmode(GPIO.BCM)
for device, state in devices.items():
    GPIO.setup(state['pin'], GPIO.OUT)

# Utworzenie nowego watku dla odczytu z czujnikow.
TempThread(7).start()

# Utworzenie aplikacji.
app = Flask(__name__)

# Doadanie rozszerzen.
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

# Konfiguracja rozszerzen.
config_app(app)

# Inicjalizacja rozszerzen.
db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
mail.init_app(app)

# Konfiguracja rozszerzen 2.
login_manager.login_view = 'login'
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Dodanie widokow.
from flask_home import routes

