from flask import Flask
from server.data import db_session

DB_NAME = 'pizzeria_base'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

if __name__ == '__main__':
    db_session.global_init(f'db/{DB_NAME}.db')
