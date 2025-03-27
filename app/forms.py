from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, DateTimeLocalField, SelectField, TextAreaField, DateField
from wtforms.validators import Email, DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username (Email)', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=30)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    fullname = StringField('Full Name', validators=[DataRequired()])
    qualification = SelectField(u'--Select Qualification', choices=[('prim_scl', 'Primary School'), ('mid_scl', 'Middle School'), ('high_scl', 'High School'), ('diploma', 'Diploma'), ('ug', 'Undergraduate'), ('pg', 'Post Graduate Degree'), ('masters', 'Masters'), ('phd', 'PhD')])
    date_of_birth = DateField('Date of Birth', format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Submit')

class SubjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

class ChapterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    submit = SubmitField

class QuizForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    date_of_quiz = DateTimeLocalField('Date of Quiz', validators=[DataRequired()])
    time_duration = IntegerField('Time Duration (In seconds)', validators=[DataRequired()])
    chapter_id = SelectField('Chapter', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

class QuestionForm(FlaskForm):
    question_statement = TextAreaField('Question', validators=[DataRequired()])
    option1 = StringField('Option 1', validators=[DataRequired()])
    option2 = StringField('Option 2', validators=[DataRequired()])
    option3 = StringField('Option 3', validators=[DataRequired()])
    option4 = StringField('Option 4', validators=[DataRequired()])
    correct_option = SelectField('Correct Option', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Question')