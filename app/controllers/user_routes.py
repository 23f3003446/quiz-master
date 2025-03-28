from app import db, login_manager
from flask import render_template, redirect, url_for, request, Blueprint, session, flash
from app.models.models import User, Subject, Chapter, Quiz, Question, Score, QuizAttempt, QuestionAttempt
from flask_login import login_user, login_required, logout_user, current_user
from app.forms import EditForm 
from random import shuffle
from sqlalchemy.sql import func, desc
from sqlalchemy.orm import aliased
import pytz 

user_bp = Blueprint('user', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def time_zone_conversion(utc_time, timezone='Asia/Kolkata'):
    if utc_time.tzinfo is None:
        utc_time = pytz.utc.localize(utc_time)
    else:
        utc_time = utc_time.astimezone(pytz.utc)

    user_timezone = pytz.timezone(timezone)
    return utc_time.astimezone(user_timezone)

@user_bp.route('/user/user_dashboard')
@login_required
def user_dashboard():
    users = User.query.all()
    form = EditForm(obj=current_user)
    scores = Score.query.filter_by(user_id=current_user.id).all()
    total_attempted_quizzes = len(scores)
    attempt = QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.time_stamp.desc()).first()

    if attempt:
        attempt.attempt_time_local = time_zone_conversion(attempt.time_stamp)

    average_score = sum([score.total_scored for score in scores]) / total_attempted_quizzes if total_attempted_quizzes > 0 else 0

    user_scores = {
        user.id: db.session.query(db.func.sum(Score.total_scored))
        .filter(Score.user_id == user.id)
        .scalar() or 0  
        for user in users
    }
    sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    total = len(users) - 1

    total_quizzes = Quiz.query.count()
    attempted_quizzes = QuizAttempt.query.filter_by(user_id = current_user.id).count()

    if attempted_quizzes:
        user_rank = next((index + 1 for index, (user_id, _) in enumerate(sorted_users) if user_id == current_user.id), None)
    else:
        user_rank = '-'

    progress_percentage = ((attempted_quizzes / total_quizzes) * 100) if total_quizzes > 0 else 0
    print(f"Total Quizzes: {total_quizzes}, Attempted Quizzes: {attempted_quizzes}, Progress: {progress_percentage}")

    return render_template("user/user_dashboard.html",
                           scores=scores,
                           total_attempted_quizzes=total_attempted_quizzes,
                           average_score=average_score,
                           user=current_user,
                           form=form,
                           user_rank=user_rank,
                           total = total,
                           progress_percentage=progress_percentage,
                           attempt=attempt)

@user_bp.route('/edit_details/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_details(id):
    user = User.query.get_or_404(id)
    form = EditForm(obj=user)
    
    if form.validate_on_submit():
        try:
            user.username = form.username.data
            user.fullname = form.fullname.data
            user.date_of_birth = form.date_of_birth.data
            user.qualification = form.qualification.data

            if form.password.data:
                user.set_password(form.password.data)

            db.session.commit()
            flash("Your details have been updated successfully!", "success")
        
        except Exception as e:
            db.session.rollback()
            flash(f"Update failed: {str(e)}", "danger")

    elif request.method == 'GET':
        form.username.data = user.username
        form.fullname.data = user.fullname
        form.date_of_birth.data = user.date_of_birth
        form.qualification.data = user.qualification

    return redirect(url_for('user.user_dashboard'))

@user_bp.route('/user/user_quizzes', methods=['GET', 'POST'])
@login_required
def user_quizzes():
    quizzes = Quiz.query.all()
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    attempted_quiz_ids = {attempt.quiz_id for attempt in QuizAttempt.query.filter_by(user_id=current_user.id).all()}
    
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        chapter_id = request.form.get('chapter_id')

        if subject_id:
            quizzes = Quiz.query.join(Chapter).filter(Chapter.subject_id == subject_id).all()
        if chapter_id:
            quizzes = Quiz.query.filter_by(chapter_id = chapter_id).all()
    
    return render_template('user/user_quizzes.html', 
                           quizzes=quizzes, 
                           subjects=subjects, 
                           chapters=chapters, 
                           attempted_quiz_ids=attempted_quiz_ids)
    
@user_bp.route('/user/user_summary')
@login_required
def user_summary():
    users = User.query.all()
    user_id = session.get("user_id")
    
    avg_score = db.session.query(func.avg(Score.total_scored)).filter(Score.user_id == current_user.id).scalar()
    avg_score = round(avg_score, 2) if avg_score else 0

    best_score = db.session.query(func.max(Score.total_scored)).filter(Score.user_id == current_user.id).scalar()
    lowest_score = db.session.query(func.min(Score.total_scored)).filter(Score.user_id == current_user.id).scalar()

    total_questions_answered = db.session.query(
        db.func.count(QuestionAttempt.id)).join(QuizAttempt, QuizAttempt.id == QuestionAttempt.quiz_attempt_id).filter(QuizAttempt.user_id == current_user.id).scalar() or 0
    
    subjects = Subject.query.all()
    subject_names = [subject.name for subject in subjects]

    subject_attempts = []
    
    for subject in subjects:
        total_attempts = (
            db.session.query(QuizAttempt)
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .join(Chapter, Quiz.chapter_id == Chapter.id)
            .filter(Chapter.subject_id == subject.id, QuizAttempt.user_id == current_user.id)
            .distinct(QuizAttempt.quiz_id)  # Count unique quiz attempts
            .count()
        )
        subject_attempts.append(total_attempts)

    attempts = []
    avg_scores = []
    
    for subject in subjects:
        attempt_count = (
            db.session.query(db.func.count(QuizAttempt.id))
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
            .join(Chapter, Quiz.chapter_id == Chapter.id)
            .filter(Chapter.subject_id == subject.id, QuizAttempt.user_id == current_user.id)
            .scalar()
        )
        avg_score = (
            db.session.query(db.func.avg(Score.total_scored))
            .join(Quiz, Score.quiz_id == Quiz.id)
            .join(Chapter, Quiz.chapter_id == Chapter.id)
            .filter(Chapter.subject_id == subject.id, Score.user_id == current_user.id)
            .scalar()
        )
        attempts.append(attempt_count if attempt_count else 0)
        avg_scores.append(round(avg_score if avg_score is not None else 0, 2))

    print("Subjects:", subject_names)
    print("Attempts:", attempts)
    print("Average Scores:", avg_scores)

    return render_template('user/user_summary.html',
                           avg_score=avg_score,
                           best_score = best_score,
                           lowest_score = lowest_score,
                           QuizAttempt=QuizAttempt,
                           total_questions_answered=total_questions_answered,
                           subjects=subject_names,
                           attempts=subject_attempts,
                           avg_scores=avg_scores
                           )

@user_bp.route('/user/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions.copy()
    ques = len(quiz.questions)

    shuffle(questions)

    if QuizAttempt.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first():
        flash("Already attempted", "warning")
        return redirect(url_for('user.user_quizzes'))
    
    if request.method == 'POST':
        score = 0
        quiz_attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=0,
        )
        db.session.add(quiz_attempt)
        db.session.commit() 

        for question in questions:
            user_answer = request.form.get(f'question_{question.id}', '0')
            is_correct = (user_answer == str(question.correct_option))

            question_attempt = QuestionAttempt(
                quiz_attempt_id=quiz_attempt.id,
                question_id=question.id,
                selected_option=user_answer,
                is_correct=is_correct
            )
            db.session.add(question_attempt)
            
            if is_correct:
                score += 1

        quiz_attempt.score = score
        
        existing_score = Score.query.filter_by(
            user_id=current_user.id, 
            quiz_id=quiz_id
        ).first()
        
        if existing_score:
            if score > existing_score.total_scored:
                existing_score.total_scored = score
        else:
            new_score = Score(
                user_id=current_user.id,
                quiz_id=quiz_id,
                total_scored=score
            )
            db.session.add(new_score)
        
        db.session.commit()

        flash(f'Quiz Completed! Your score: {score}/{len(questions)}', "success")
        return redirect(url_for('user.quiz_results', quiz_id=quiz_id))
    
    return render_template('user/attempt_quiz.html', 
                           quiz=quiz, 
                           questions=questions, 
                           ques=ques)

@user_bp.route('/user/quiz_results/<int:quiz_id>') 
@login_required
def quiz_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    attempts = QuizAttempt.query.all()
    quiz_attempt = QuizAttempt.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).order_by(QuizAttempt.time_stamp.desc()).first()

    score = quiz_attempt.score if quiz_attempt else 0
    for attempt in attempts:
        attempt.attempt_time_local = time_zone_conversion(attempt.time_stamp)

    if not quiz_attempt:
        return "No quiz attempt found!", 404
    
    user_attempts = QuestionAttempt.query.filter_by(quiz_attempt_id=quiz_attempt.id).all()

    user_answers = {attempt.question_id: attempt.selected_option for attempt in user_attempts}

    results = []
    for question in questions:
        option1 = question.option1
        option2 = question.option2
        option3 = question.option3
        option4 = question.option4
        correct_option = question.correct_option  
        user_answer = user_answers.get(question.id, "Not Answered")

        results.append({
            "question": question.question_statement,
            "user_answer": int(user_answers.get(question.id, 0)), 
            "option1": question.option1,
            "option2": question.option2,
            "option3": question.option3,
            "option4": question.option4,
            "correct_answer": int(correct_option),                
            "is_correct": int(user_answers.get(question.id, 0)) == int(correct_option)
        })


    return render_template('user/quiz_results.html', 
                           quiz=quiz, 
                           score=score, 
                           questions=questions,
                           results=results, 
                           attempts=attempts,
                           attempt=attempt)

@user_bp.route('/user/leaderboard')
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
    return render_template('user/leaderboard.html', 
                           leaderboard=leaderboard,
                           user_fullnames = user_fullnames,
                           user_total_scores = user_total_scores
                           )