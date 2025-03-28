from app import db, login_manager
from flask import render_template, redirect, flash, url_for, request, Blueprint, session
from app.forms import LoginForm, RegistrationForm
from app.models.models import User
from flask_login import login_user, login_required, logout_user, current_user
import os
import random

authentication_bp = Blueprint('auth', __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROFILE_IMAGES_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'profiles')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@authentication_bp.route('/')
def home():
    return render_template('common/home.html')

@authentication_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username = form.username.data).first()

        if existing_user:
            flash("Username taken! Please enter a different username!", "danger")
            return redirect(url_for('auth.register'))
        
        if form.username.data.lower() == "admin@quizmaster.com":
            flash("Username not allowed!", "danger")
            return redirect(url_for('auth.register'))
        
        profile_images = [file for file in os.listdir(PROFILE_IMAGES_FOLDER) if file.endswith('.png')]
        profile_image = random.choice(profile_images)

        user = User(username = form.username.data,
                    fullname = form.fullname.data,
                    qualification = form.qualification.data,
                    date_of_birth = form.date_of_birth.data,
                    is_admin = False,
                    profile_image = profile_image
                )
        
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account Registered Successfully!", "success")
        return redirect(url_for('auth.login'))
    return render_template('common/register.html', form=form)

@authentication_bp.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()

        if user and user.query.filter_by(username = form.username.data):
            login_user(user)
            flash("Login Successfully!", "success")

            if user.is_admin:
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.user_dashboard'))
            
        else:
            flash("Authentication Failed! Please check your credentials.", "danger")
    return render_template('common/login.html', form=form)

@authentication_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logged Out Successfully!", "success")
    return redirect(url_for('auth.home'))


