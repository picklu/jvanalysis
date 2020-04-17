# *************************************************
# Modified from
# Book: Flask: Building Python Web Services
# By Gareth Dwyer, Shalabh Aggarwal, Jack Stouffer
# *************************************************
from flask_wtf import FlaskForm
from wtforms import (PasswordField, SubmitField, validators, HiddenField)
from wtforms.fields.html5 import EmailField


class SignupForm(FlaskForm):
    email = EmailField('email',
                       validators=[
                           validators.DataRequired("Email field is required"),
                           validators.Email()
                       ])
    password = PasswordField(
        'password',
        validators=[
            validators.DataRequired("Password field is required"),
            validators.Length(
                min=4,
                message="Please choose a password of at least 4 characters")
        ])
    password2 = PasswordField(
        'password2',
        validators=[
            validators.DataRequired("Confirm password field is required"),
            validators.EqualTo('password', message='Passwords must match')
        ])
    submit = SubmitField('submit', [validators.DataRequired()])


class SigninForm(FlaskForm):
    next = HiddenField('next')
    email = EmailField('email',
                       validators=[
                           validators.DataRequired("Email field is required"),
                           validators.Email()
                       ])
    password = PasswordField(
        'password',
        validators=[
            validators.DataRequired(message="Password field is required")
        ])
    submit = SubmitField('submit', [validators.DataRequired()])
