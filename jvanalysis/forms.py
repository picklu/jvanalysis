# *************************************************
# Modified from
# Book: Flask: Building Python Web Services
# By Gareth Dwyer, Shalabh Aggarwal, Jack Stouffer
# *************************************************
from flask_wtf import FlaskForm
from wtforms import (PasswordField, SubmitField, validators, TextField)
from wtforms.fields.html5 import EmailField

class SignupForm(FlaskForm):
    email = EmailField('email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('password', validators=[validators.DataRequired(), validators.Length(min=4, message="Please choose a password of at least 8 characters")])
    password2 = PasswordField('password2', validators=[validators.DataRequired(), validators.EqualTo('password', message='Passwords must match')])
    submit = SubmitField('submit', [validators.DataRequired()])


class SigninForm(FlaskForm):
    email = EmailField('email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('password', validators=[validators.DataRequired(message="Password field is required")])
    submit = SubmitField('submit', [validators.DataRequired()])