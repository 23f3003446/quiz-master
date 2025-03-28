from app import db, login_manager
from flask import render_template, redirect, url_for, request, Blueprint, flash
from flask_login import login_user, login_required, current_user
from app.models.models import User, Subject, Chapter, Quiz, Question, Score, QuizAttempt, QuestionAttempt
from app.forms import SubjectForm, ChapterForm, QuizForm, QuestionForm
from sqlalchemy.sql import func, desc
from sqlalchemy.orm import aliased

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("You don't have access to this page!", "danger")
        return redirect(url_for('user.user_dashboard'))
    return render_template('admin/admin_dashboard.html')

@admin_bp.route('/admin/subjects', methods=['GET', 'POST'])
@login_required
def subjects():
    if not current_user.is_admin:
        flash("You don't have access to this page!", "danger")
        return redirect(url_for('auth.home'))
    
    subjects = Subject.query.all()
    form = SubjectForm()
    edit_forms = {subject.id : SubjectForm(obj=subject) for subject in subjects}

    search_query = request.args.get('subject_name','').strip()

    if search_query:
        subjects = Subject.query.filter(Subject.name.ilike(f'%{search_query}%')).all()

    if form.validate_on_submit():
        subject = Subject(name = form.name.data,
                          description = form.description.data)
        db.session.add(subject)
        db.session.commit()
        flash("Subject Added Successfully!", "success")
        return redirect(url_for('admin.subjects'))
    return render_template('admin/subjects.html',
                           subjects=subjects,
                           form=form,
                           edit_forms=edit_forms,
                           search_query=search_query)

@admin_bp.route('/admin/edit_subject/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_subject(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('auth.home'))
    
    subject = Subject.query.get_or_404(id)
    form=SubjectForm(obj=subject)
    if form.validate_on_submit():
        subject.name = form.name.data
        subject.description = form.description.data
        db.session.commit()
        flash("Subject details succesfully updated!")
        return redirect(url_for('admin.subjects'))
    return render_template('admin/subjects.html', form=form, subjects=subjects)

@admin_bp.route('/admin/delete_subject/<int:id>', methods=['POST'])
@login_required
def delete_subject(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('auth.home'))
    subject = Subject.query.get_or_404(id)

    chapters = Chapter.query.filter_by(subject_id=id).all()

    for chapter in chapters:
        quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()

        for quiz in quizzes:
            QuestionAttempt.query.filter(
                QuestionAttempt.question_id.in_(
                    [question.id for question in quiz.questions]
                )
            ).delete(synchronize_session=False)

            Score.query.filter_by(quiz_id=quiz.id).delete()
            QuizAttempt.query.filter_by(quiz_id=quiz.id).delete()
            Question.query.filter_by(quiz_id=quiz.id).delete()

            db.session.delete(quiz)
        db.session.delete(chapter)
    db.session.delete(subject)

    db.session.commit()
    return redirect(url_for('admin.subjects'))

@admin_bp.route('/admin/chapters', methods=['GET', 'POST'])
@login_required
def chapters():
    if not current_user.is_admin:
        flash("You don't have access to this page!", "danger")
        return redirect(url_for('auth.home'))
    
    chapters = Chapter.query.all()
    
    form = ChapterForm()
    edit_forms = {chapter.id : ChapterForm(obj=chapter) for chapter in chapters}

    search_query = request.args.get('chapter_name', '')

    if search_query:
        chapters = Chapter.query.filter(Chapter.name.ilike(f'%{search_query}%')).all()

    form.subject_id.choices = [(subject.id, subject.name) for subject in Subject.query.all()]

    if form.validate_on_submit():
        chapter = Chapter(name = form.name.data,
                          description = form.description.data,
                          subject_id = form.subject_id.data)
        db.session.add(chapter)
        db.session.commit()
        flash("Chapter Successfully Added", "success")
        return redirect(url_for('admin.chapters'))
    return render_template('admin/chapters.html',
                           chapters=chapters,
                           form=form,
                           edit_forms=edit_forms,
                           search_query=search_query)

@admin_bp.route('/admin/edit_chapter/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_chapter(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!", "danger")
        return redirect(url_for('auth.home'))
    chapter = Chapter.query.get_or_404(id)
    form=ChapterForm(obj=chapter)
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.all()]
    
    if form.validate_on_submit():
        chapter.name = form.name.data
        chapter.description = form.description.data
        chapter.subject_id = form.subject_id.data
        db.session.commit()
        flash("Chapter details updated successfulyy!", "success")
        return redirect(url_for('admin.chapters'))
    return render_template('admin/chapters.html', form=form)

@admin_bp.route('/admin/delete_chapter/<int:id>', methods=['POST'])
@login_required
def delete_chapter(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!", "danger")
        return redirect(url_for('auth.home'))
    chapter = Chapter.query.get_or_404(id)

    quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()

    for quiz in quizzes:
        QuestionAttempt.query.filter(
            QuestionAttempt.question_id.in_(
                [q.id for q in quiz.questions]
            )
        ).delete(synchronize_session=False)

        Score.query.filter_by(quiz_id=quiz.id).delete()

        QuizAttempt.query.filter_by(quiz_id=quiz.id).delete()

        Question.query.filter_by(quiz_id=quiz.id).delete()

        db.session.delete(quiz)

    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('admin.chapters'))

@admin_bp.route('/admin/quizzes', methods=['GET', 'POST'])
@login_required
def quizzes():
    if not current_user.is_admin:
        flash("You don't have access to this page!", "danger")
        return redirect(url_for('auth.home'))
    
    quizzes = Quiz.query.all()
    edit_forms = {quiz.id : QuizForm(obj=quiz) for quiz in quizzes}
    
    form = QuizForm()
    form.chapter_id.choices = [(chapter.id, chapter.name) for chapter in Chapter.query.all()]

    search_query = request.args.get('quiz_name', '')

    if search_query:
        quizzes= Quiz.query.filter(Quiz.name.ilike(f'%{search_query}')).all()

    if form.validate_on_submit():
        quiz= Quiz(
            name = form.name.data,
            date_of_quiz = form.date_of_quiz.data,
            time_duration = form.time_duration.data,
            chapter_id = form.chapter_id.data
        )
        db.session.add(quiz)
        db.session.commit()
        flash("Quiz Added Successfully!", "success")
        return redirect(url_for('admin.quizzes'))
    return render_template('admin/quizzes.html',
                           quizzes=quizzes,
                           form=form,
                           edit_forms=edit_forms,
                           search_query=search_query)

@admin_bp.route('/admin/edit_quiz/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('auth.home'))
    quiz = Quiz.query.get_or_404(id)
    form=QuizForm(obj=quiz)
    form.chapter_id.choices = [(c.id, c.name) for c in Chapter.query.all()]
    if form.validate_on_submit():
        quiz.name = form.name.data
        quiz.date_of_quiz = form.date_of_quiz.data
        quiz.time_duration = form.time_duration.data
        quiz.chapter_id = form.chapter_id.data
        db.session.commit()
        flash("Quiz details updated successfulyy!")
        return redirect(url_for('admin.quizzes'))
    return render_template('admin/quizzes.html', form=form)

@admin_bp.route('/admin/delete_quiz/<int:id>', methods=['POST'])
@login_required
def delete_quiz(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('auth.home'))
    quiz = Quiz.query.get_or_404(id)

    QuestionAttempt.query.filter(
        QuestionAttempt.question_id.in_(
            [q.id for q in quiz.questions]
        )
    ).delete(synchronize_session=False)

    Score.query.filter_by(quiz_id=id).delete()

    QuizAttempt.query.filter_by(quiz_id=id).delete()

    Question.query.filter_by(quiz_id=id).delete()

    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('admin.quizzes'))

@admin_bp.route('/admin/questions/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def questions(quiz_id):
    if not current_user.is_admin:
        flash("You don't have access to this page!", "danger")
        return redirect(url_for('auth.home'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = quiz.questions

    form = QuestionForm()
    edit_forms = {question.id : QuestionForm(obj=question) for question in questions}

    if form.validate_on_submit():
        question = Question(
            question_statement = form.question_statement.data,
            option1 = form.option1.data,
            option2 = form.option2.data,
            option3 = form.option3.data,
            option4 = form.option4.data,
            correct_option = int(form.correct_option.data),
            quiz_id = quiz_id
        )
        db.session.add(question)
        db.session.commit()
        flash("Question Added Successfully!", "success")
        return redirect(url_for('admin.questions', quiz_id=quiz_id))
    return render_template('admin/questions.html', 
                           quiz=quiz, 
                           questions=questions, 
                           form=form, 
                           edit_forms=edit_forms)

@admin_bp.route('/admin/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    if not current_user.is_admin:
        flash("You don't have access to this page!", "success")
        return redirect(url_for('home'))
    question = Question.query.get_or_404(question_id)
    form = QuestionForm(obj=question)
    
    if form.validate_on_submit():
        question.question_statement = form.question_statement.data
        question.option1 = form.option1.data
        question.option2 = form.option2.data
        question.option3 = form.option3.data
        question.option4 = form.option4.data
        question.correct_option = form.correct_option.data
        db.session.commit()
        flash("Question edited.")
        return redirect(url_for('admin.questions', quiz_id=question.quiz_id))
    return render_template('admin/edit_question.html', form=form)

@admin_bp.route('/admin/delete_question/<int:id>', methods=['POST'])
@login_required
def delete_question(id):
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('auth.home'))
    
    question = Question.query.get_or_404(id)
    if not question:
        flash("Question not found!")
        return redirect(url_for('auth.home'))

    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('admin.questions', quiz_id=question.quiz_id))

@admin_bp.route('/admin/users')
@login_required
def users():
    if not current_user.is_admin:
        flash("You don't have access to this page!")
        return redirect(url_for('auth.home'))
    
    users = User.query.all()
    total_quizzes = Quiz.query.count()
    user_stats = {}

    search_query = request.args.get('user_name', '').strip().lower()

    if search_query:
        users = User.query.filter(func.lower(User.fullname).ilike(f'%{search_query}')).all()

    for user in users:
        attempted_quizzes = QuizAttempt.query.filter_by(user_id=user.id).count()

        avg_score = db.session.query(func.avg(Score.total_scored)).filter(Score.user_id==user.id).scalar()
        best_score = db.session.query(func.max(Score.total_scored)).filter(Score.user_id==user.id).scalar()
        lowest_score = db.session.query(func.min(Score.total_scored)).filter(Score.user_id==user.id).scalar()

        user_stats[user.id] = {
            "name": user.fullname,
            "email": user.username,
            "attempted_quizzes": attempted_quizzes,
            "avg_score": round(avg_score, 2) if avg_score else 0,
            "best_score": best_score,
            "lowest_score": lowest_score
        }

    if request.method =='POST':
        user_fullname = request.form.get('user_fullname')

        if user_fullname:
            user = User.query.filter_by(user_fullname=user_fullname).all()
    
    return render_template('admin/users.html', users=users,
                           user_stats=user_stats,
                           total_quizzes=total_quizzes, 
                           search_query=search_query)

@admin_bp.route('/admin/summary')
@login_required
def admin_summary():
    quizzes = Quiz.query.all()
    quiz_names = [quiz.name for quiz in quizzes]
    average_scores = []
    completion_rates = []

    for quiz in quizzes:
        scores = Score.query.filter_by(quiz_id = quiz.id).all()
        if scores:
            average_score = sum([score.total_scored for score in scores]) / len(scores)
            users_attempted = len(scores)
            completion_rate = (users_attempted / (User.query.count() - 1)) * 100
        else:
            average_score = 0
            completion_rate = 0
        average_scores.append(average_score)
        completion_rates.append(completion_rate)

    subquery = (
        db.session.query(
            Subject.id.label("subject_id"),
            func.max(Score.total_scored).label("top_score")
        )
        .join(Chapter, Chapter.subject_id== Subject.id)
        .join(Quiz, Quiz.chapter_id == Chapter.id)
        .join(Score, Score.quiz_id == Quiz.id)
        .group_by(Subject.id)
        .subquery()
    )

    top_scores = (
        db.session.query(
            Subject.name.label("subject_name"),
            User.fullname.label("user_fullname"),
            Score.total_scored.label("top_score")
        )
        .join(Quiz, Quiz.id == Score.quiz_id)
        .join(Chapter, Chapter.id == Quiz.chapter_id)
        .join(Subject, Subject.id == Chapter.subject_id)
        .join(User, User.id == Score.user_id)
        .join(subquery, (subquery.c.subject_id == Subject.id) & (subquery.c.top_score == Score.total_scored))
        .order_by(Subject.name)
        .all()
    )

    chapter_alias = aliased(Chapter)

    subject_wise_attempts = (
        db.session.query(
            Subject.name.label("subject_name"),
            func.count(QuizAttempt.id).label("total_attempts")
        )
        .select_from(Subject)
        .join(chapter_alias, Subject.id == chapter_alias.subject_id)
        .join(Quiz, chapter_alias.id == Quiz.chapter_id)
        .join(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)
        .group_by(Subject.name)
        .all()
    )

    subject_names = [row.subject_name for row in subject_wise_attempts]
    attempts_data = [row.total_attempts for row in subject_wise_attempts]

    subjects = [entry.subject_name for entry in top_scores]
    scores = [entry.top_score for entry in top_scores]
    users = [entry.user_fullname for entry in top_scores]

    return render_template('admin/admin_summary.html', 
                           quiz_names=quiz_names, 
                           average_scores=average_scores, 
                           completion_rates=completion_rates,
                           top_scores=top_scores,
                           subject_wise_attempts=subject_wise_attempts,
                           subject_names=subject_names,
                           attempts_data=attempts_data,
                           subjects=subjects,
                           users=users,
                           scores=scores)

@admin_bp.route("/admin/user_stats")
@login_required
def user_stats():
    users = User.query.all()
    total_quizzes = Quiz.query.count()
    
    user_stats = {}
    for user in users:
        avg_score = db.session.query(func.avg(Score.total_scored)).filter(Score.user_id == user.id).scalar() or 0
        best_score = db.session.query(func.max(Score.total_scored)).filter(Score.user_id == user.id).scalar() or 0
        lowest_score = db.session.query(func.min(Score.total_scored)).filter(Score.user_id == user.id).scalar() or 0
        quizzes_attempted = QuizAttempt.query.filter_by(user_id=user.id).count()

        user_stats[user.id] = {
            "avg_score": round(avg_score),
            "best_score": best_score,
            "lowest_score": lowest_score,
            "quizzes_attempted": quizzes_attempted,
        }

    return render_template("admin/users.html", users=users, user_stats=user_stats, total_quizzes=total_quizzes)