from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SECRET_KEY'] = "myseckey"      
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///quiz_master.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    return app

