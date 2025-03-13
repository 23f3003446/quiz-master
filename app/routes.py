from app import create_app, db, login_manager
from flask import render_template, redirect, flash, url_for, session
from app.forms import RegisterForm, LoginForm
from app.models import User, Subject, Chapter, Quiz, Question, Score
from flask_login import login_user, login_required, logout_user, current_user

app = create_app()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.cli.command('db-create')
def create_db():
    db.create_all()
    admin = User.query.filter_by(username="admin@quizmaster.com")
    if not admin:
        admin = User(
            username = "admin@quizmaster.com",
            fullname = "Quiz Master Admin",
            is_admin = True
        )
        admin.set_password("admin12345")
        db.session.add(admin)
        db.session.commit()
        print("Admin created!")
    else:
        print("Admin already exists!")
    print("DB Created")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.username.data.lower() == "admin@quizmaster.com":
            flash("Username not allowed!")
            return redirect(url_for('register'))
        user = User (username = form.username.data,
                    fullname = form.fullname.data,
                    qualification = form.qualification.data,
                    date_of_birth = form.date_of_birth.data,
                    is_admin = False
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Account registration successful!")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login Successful!')

            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash("Authentication Failed!")
    return render_template('login.html', form=form)

@app.route('/user_dashboard')
@login_required
def dashboard():
    return render_template('user_dashboard.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('user_dashboard'))
    return render_template('admin_dashboard.html')

@app.route('/admin/subjects')
@login_required
def manage_subjects():
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    subjects = Subject.query.all()
    return render_template('subjects.html', subjects=subjects)

@app.route('/admin/chapters')
@login_required
def manage_chapters():
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    chapters = Chapter.query.all()
    return render_template('chapters.html', chapters=chapters)

@app.route('/admin/quizzes')
@login_required
def manage_quizzes():
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    quizzes = Quiz.query.all()
    return render_template('quizzes.html', quizzes=quizzes)

@app.route('/admin/questions')
@login_required()
def manage_questions():
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    questions = Question.query.all()
    return render_template('questions.html', questions=questions)

@app.route('/admin/scores')
@login_required
def manage_scores():
    if not current_user.is_admin():
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    scores = Score.query.all()
    return render_template('scores.html', scores=scores)

@app.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('users.html', users = users)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logout successful!")
    return redirect(url_for('home'))



