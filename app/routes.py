from app import create_app, db, login_manager
from flask import render_template, redirect, flash, url_for, session, request
from app.forms import RegisterForm, LoginForm, SubjectForm, ChapterForm, QuizForm, QuestionForm
from app.models import User, Subject, Chapter, Quiz, Question, Score
from flask_login import login_user, login_required, logout_user, current_user
from random import shuffle

app = create_app()

@login_manager.user_loader 
def load_user(user_id): 
    return User.query.get(user_id)

@app.route('/')
def home():
    return render_template('common/home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login Successful!", "success")

            if user.is_admin:
                return redirect(url_for('admin/admin_dashboard'))
            else:
                return redirect(url_for('user/user_dashboard'))
        else:
            flash("Authentication failed!", "failure")
    return render_template('common/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if form.username.data.lower() == "admin@quizmaster.com":
            flash("Username not allowed!")
            return redirect(url_for('register'))
        user = User(username = form.username.data,
                    fullname = form.fullname.data,
                    qualification = form.qualification.data,
                    date_of_birth = form.date_of_birth.data,
                    is_admin = False
                )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account Registration successful!')
        return redirect(url_for('login'))
    return render_template('common/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logout Successful")
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('user_dashboard'))
    return render_template('admin/admin_dashboard.html')

@app.route('/admin/subjects')
@login_required
def manage_subjects():
    if current_user.username != "admin@quizmaster.com":
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

@app.route('/admin/chapters')
@login_required
def manage_chapters():
    if current_user.username != "admin@quizmaster.com":
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    chapters = Chapter.query.all()
    return render_template('admin/chapters.html', chapters=chapters)

@app.route('/admin/quizzes')
@login_required
def manage_quizzes():
    if current_user.username != "admin@quizmaster.com":
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    quizzes = Quiz.query.all()
    return render_template('admin/quizzes.html', quizzes=quizzes)

@app.route('/admin/questions')
@login_required
def manage_questions():
    if current_user.username != "admin@quizmaster.com":
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    questions = Question.query.all()
    return render_template('admin/questions.html', questions=questions)

@app.route('/admin/users')
@login_required
def manage_users():
    if current_user.username != "admin@quizmaster.com":
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/scores')
@login_required
def manage_scores():
    if current_user.username != "admin@quizmaster.com":
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    scores = Score.query.all()
    return render_template('admin/scores.html', scores=scores)

@app.route('/admin/summary')
@login_required
def admin_summary():
    quizzes = Quiz.query.all()
    quiz_names = [quiz.name for quiz in quizzes]
    average_scores = []
    completion_rates = []
    for quiz in quizzes:
        scores = Score.query.filter_by(quiz_id = quiz.id).all()
        if scores:
            average_score = sum([s.total_scored for s in scores]) / len(scores)
            users_attempted = len(scores)
            completion_rate = (users_attempted / (User.query.count() - 1)) * 100
        else:
            average_score = 0
            completion_rate = 0
        average_scores.append(average_score)
        completion_rates.append(completion_rate)
        
    return render_template('admin/admin_summary.html', 
                           quiz_names=quiz_names, 
                           average_scores=average_scores, 
                           completion_rates=completion_rates)

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    scores = Score.query.filter_by(user_id=current_user.id).all()
    total_attempted_quizzes = len(scores)

    average_score = sum([s.total_scored for s in scores]) / total_attempted_quizzes if total_attempted_quizzes > 0 else 0

    return render_template("user/user_dashboard.html",
                           scores=scores,
                           total_attempted_quizzes=total_attempted_quizzes,
                           average_score=average_score)

@app.route('/user_quizzes')
@login_required
def user_quizzes():
    quizzes = Quiz.query.all()
    return render_template('user/user_quizzes.html', quizzes=quizzes)

@app.route('/user_summary')
@login_required
def user_summary():
    return render_template('user/user_summary.html')

@app.route('/admin/add_subject', methods=['GET','POST'])
@login_required
def add_subject():
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    form=SubjectForm()
    if form.validate_on_submit():
        subject = Subject(name=form.name.data, description=form.description.data)
        db.session.add(subject)
        db.session.commit()
        flash("Subject successfully added!")
        return redirect(url_for('manage_subjects'))
    return render_template('admin/add_subject.html', form=form)

@app.route('/admin/edit_subject/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subject(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    subject = Subject.query.get_or_404(id)
    form=SubjectForm(obj=subject)
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash("Subject details succesfully updated!")
        return redirect(url_for('manage_subjects'))
    return render_template('admin/edit_subject.html', form=form)

@app.route('/admin/delete_subject/<int:id>', methods=['POST'])
@login_required
def delete_subject(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('manage_subjects'))

@app.route('/admin/add_chapter', methods=['GET', 'POST'])
@login_required
def add_chapter():
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    form = ChapterForm()
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        chapter = Chapter(
            name=form.name.data, 
            description=form.description.data,
            subject_id = form.subject_id.data
        )
        db.session.add(chapter)
        db.session.commit()
        flash("Chapter successfully added!")
        return redirect(url_for('manage_chapters'))
    return render_template('admin/add_chapter.html', form=form)

@app.route('/admin/edit_chapter/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_chapter(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    chapter = Chapter.query.get_or_404(id)
    form=ChapterForm(obj=chapter)
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    if form.validate_on_submit():
        chapter.name = form.name.data
        chapter.description = form.description.data
        chapter.subject_id = form.subject_id.data
        db.session.commit()
        flash("Chapter details updated successfulyy!")
        return redirect(url_for('manage_chapters'))
    return render_template('admin/edit_chapter.html', form=form)

@app.route('/admin/delete_chapter/<int:id>', methods=['POST'])
@login_required
def delete_chapter(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    chapter = Chapter.query.get_or_404(id)
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('manage_chapters'))

@app.route('/admin/add_quiz', methods=['GET', 'POST'])
@login_required
def add_quiz():
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    form = QuizForm()
    form.chapter_id.choices = [(c.id, c.name) for c in Chapter.query.all()]
    if form.validate_on_submit():
        quiz = Quiz(
            name = form.name.data,
            date_of_quiz = form.date_of_quiz.data,
            time_duration = form.time_duration.data,
            chapter_id = form.chapter_id.data
        )
        db.session.add(quiz)
        db.session.commit()
        flash("Quiz successfully added!")
        return redirect(url_for('manage_quizzes'))
    return render_template('admin/add_quiz.html', form=form)

@app.route('/admin/edit_quiz/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    quiz = Quiz.query.get_or_404(id)
    form=QuizForm(obj=quiz)
    form.chapter_id.choices = [(c.id, c.name) for c in Chapter.query.all()]
    if form.validate_on_submit():
        quiz.name = form.name.data,
        quiz.date_of_quiz = form.date_of_quiz.data
        quiz.time_duration = form.time_duration.data
        quiz.chapter_id = form.chapter_id.data
        db.session.commit()
        flash("Quiz details updated successfulyy!")
        return redirect(url_for('manage_quizzes'))
    return render_template('admin/edit_quiz.html', form=form)

@app.route('/admin/delete_quiz/<int:id>', methods=['POST'])
@login_required
def delete_quiz(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    quiz = Quiz.query.get_or_404(id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('manage_quizzes'))

@app.route('/admin/manage_quiz_questions/<int:quiz_id>')
@login_required
def manage_quiz_questions(quiz_id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions
    return render_template('admin/manage_quiz_questions.html', quiz=quiz, questions=questions)

@app.route('/admin/add_question/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def add_question(quiz_id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('home'))
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question (
            question_statement = form.question_statement.data,
            option1 = form.option1.data,
            option2 = form.option2.data,
            option3 = form.option3.data,
            option4 = form.option4.data,
            correct_option = form.correct_option.data,
            quiz_id = quiz_id
        )
        db.session.add(question)
        db.session.commit()
        flash("Question successfully added!")
        return redirect(url_for('manage_quiz_questions', quiz_id=quiz_id))
    return render_template('admin/add_question.html', form=form, quiz=Quiz)

@app.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions.copy()
    shuffle(questions)
    if request.method =='POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')

            if user_answer and int(user_answer) == int(question.correct_option):
                score = score + 1

        user_score = Score(
            total_scored = score,
            quiz_id = quiz_id,
            user_id = current_user.id
        )
        db.session.add(user_score)
        db.session.commit()
        print(f"Score saved for user {current_user.id} in quiz {quiz_id}: {score}")

        flash(f'Quiz Completed! Your score: {score} / {len(questions)}')
        return redirect(url_for('quiz_results', quiz_id = quiz_id))
    return render_template('user/attempt_quiz.html', quiz=quiz, questions=questions)

@app.route('/quiz_results/<int:quiz_id>')
@login_required
def quiz_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(user_id = current_user.id, quiz_id=quiz_id).first()
    return render_template('user/quiz_results.html', quiz=quiz, score=score)

@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.get_users()
    leaderboard = []
    for user in users:
        scores = Score.query.filter_by(user_id=user.id).all()
        total_score = sum([s.total_scored for s in scores])
        leaderboard.append({
            "user_fullname": user.fullname,
            "total_score": total_score
        })
    leaderboard.sort(key=lambda x: x['total_score'], reverse=True)
    user_fullnames = [x['user_fullname'] for x in leaderboard]
    user_total_scores = [x['total_score'] for x in leaderboard]
    return render_template('leaderboard.html', 
                           leaderboard=leaderboard,
                           user_fullnames = user_fullnames,
                           user_total_scores = user_total_scores
                           )

@app.route('/select_quiz', methods=['GET', 'POST'])
@login_required
def select_quiz():
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        chapter_id = request.form.get('chapter_id')

        if subject_id:
            quizzes = Quiz.query.join(Chapter).filter(Chapter.subject_id == subject_id).all()
        if chapter_id:
            quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
            
    return render_template('user/select_quiz.html', subjects=subjects, chapters=chapters, quizzes=quizzes)