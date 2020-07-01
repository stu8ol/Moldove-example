from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.models import User
from app import photos


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class CreateGame(FlaskForm):
	noof_players = IntegerField('How many players?', validators=[DataRequired()])
	submit = SubmitField('Create')

class JoinGame(FlaskForm):
	game_id = StringField('Enter the game ID of the game you want to join')
	submit= SubmitField('Join')
	
class EnterName(FlaskForm):
	player_name = StringField('Please enter your name and press ready when you want to start the game.')
	submit= SubmitField('Ready!')
	
class PlayAgain(FlaskForm):
	submit= SubmitField('Play Again')
	
class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address.')

class UploadForm(FlaskForm):
    photo = FileField(validators=[FileAllowed(photos, 'Image Only!'), FileRequired('Choose a file!')])
    submit = SubmitField('Upload')
