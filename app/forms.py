from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField, TextAreaField, SelectField, DateTimeLocalField, IntegerField
from wtforms.validators import Email, Length, EqualTo, DataRequired, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Username (Email)', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=30)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    fullname = StringField('Full Name', validators=[DataRequired()])
    qualification = SelectField('Qualification', choices=[('', '--Select Qualification'),
                                                          ('High School', 'High School'), 
                                                          ('Diploma', 'Diploma'), 
                                                          ('UnderGraduate', 'Undergraduate'), 
                                                          ('PostGraduate', 'Post Graduate Degree'), 
                                                          ('Masters', 'Masters'), 
                                                          ('PhD', 'PhD')])
    date_of_birth = DateField('Date of Birth', format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Submit')

class SubjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Submit')

class ChapterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

class QuizForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    date_of_quiz = DateTimeLocalField('Date of Quiz', validators=[DataRequired()])
    time_duration = IntegerField('Time Duration (In seconds)', validators=[DataRequired()])
    chapter_id = SelectField('Chapter', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

class QuestionForm(FlaskForm):
    question_statement = TextAreaField('Question Statement', validators=[DataRequired()])
    option1 = StringField('Option 1', validators=[DataRequired()])
    option2 = StringField('Option 2', validators=[DataRequired()])
    option3 = StringField('Option 3', validators=[DataRequired()])
    option4 = StringField('Option 4', validators=[DataRequired()])
    correct_option = SelectField('Correct Option', choices=[('', '--Select Correct Option'), 
                                                            ('1', 'Option 1'),
                                                            ('2', 'Option 2'), 
                                                            ('3', 'Option 3'), 
                                                            ('4', 'Option 4')], 
                                                            validators=[DataRequired()])
    submit = SubmitField('Save')

class EditForm(FlaskForm):
    username = StringField('Username (Email)', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[Optional()])
    fullname = StringField('Full Name', validators=[DataRequired()])
    qualification = SelectField('Qualification', choices=[('', '--Select Qualification'),
                                                          ('High School', 'High School'), 
                                                          ('Diploma', 'Diploma'), 
                                                          ('UnderGraduate', 'Undergraduate'), 
                                                          ('PostGraduate', 'Post Graduate Degree'), 
                                                          ('Masters', 'Masters'), 
                                                          ('PhD', 'PhD')])
    date_of_birth = DateField('Date of Birth', format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField('Submit')