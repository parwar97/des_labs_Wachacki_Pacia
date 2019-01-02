from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import RPi.GPIO as GPIO


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/html/firstapp/flask_home/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail()


# Konfiguracja wyjsc RPI.
GPIO.setmode(GPIO.BCM)

devices = {
    'lamp':{'id':1, 'pin':26, 'state':GPIO.LOW},
    'electricity':{'id':2, 'pin':19, 'state':GPIO.LOW},
    'door':{'id':3, 'pin':23, 'state':GPIO.LOW},
}

for device, state in devices.items():
    GPIO.setup(state['pin'], GPIO.OUT)



#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/html/firstapp/flask_home/site.db'
app.config['SECRET_KEY'] = '9da539cebcb6ab591de53483af7b0cf8'
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "pibermaw@gmail.com"#os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = "serwermaras22."#os.environ.get('EMAIL_PASS')
mail.init_app(app)
login_manager.login_view = 'login'




from flask_home import routes

