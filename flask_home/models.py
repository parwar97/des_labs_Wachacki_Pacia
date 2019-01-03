"""
Plik z modelami uzytkownikow.
"""

from flask_home import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


# Ladowanie uzytkowniak.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """
    Model uzytkownika.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)

    def get_reset_token(self, expires_sec=1800):
        """
        Metoda generujaca token unikalnego adresu URL.

        :param expires_sec: Czas, po ktorym token wygasnie (w sekundach)
        :return: Token
        """

        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
         """
        Metoda sprawdzajaca waznosc tokenu.

        :param token: Token
        :return: Uzytkownik, ktory wygenerowal token
        """

        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


    def __repr__(self):
        return "User('%s', '%s', '%s')" % (self.username, self.email, self.image_file)

