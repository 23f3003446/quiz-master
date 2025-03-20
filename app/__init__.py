from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv() 

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.secret_key = os.getenv("SECRET_KEY", "myseckey")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///project.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app import models
    from app.models import User

    with app.app_context():
        if not os.path.exists("project.db"):
            db.create_all()
            print("DB created successfully!")
            admin = User.query.filter_by(username="admin@quizmaster.com").first()
            if not admin:
                admin = User(
                    username = "admin@quizmaster.com",
                    fullname = "Quiz Master Admin",
                    is_admin = True
                )
                admin.set_password("admin12345")
                db.session.add(admin)
                db.session.commit()
                print("Admin created successfully.")
    return app