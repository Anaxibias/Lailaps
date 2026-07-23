from flask import flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, URL, Regexp
import sqlalchemy as sa
from app import db
from app.models import User, Job, UserJob

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError('Username already taken.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('An account already exists for this email address. Please sign in or use a different email address')
        
class JobUrlForm(FlaskForm):
    url = StringField('Enter job URL', validators=[DataRequired(), URL(message="Invalid URL"), Regexp(r'^https://.*', message='URL Not Secure')])
    submit = SubmitField('Save Job')

class InfoForm(FlaskForm):
    job_title = StringField('Enter job title', validators=[DataRequired()])
    job_company = StringField('Enter company', validators=[DataRequired()])
    submit = SubmitField('Add Job')
