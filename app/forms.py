from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField
from wtforms.validators import ValidationError, DataRequired, EqualTo, NumberRange, InputRequired
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat password:', validators=[DataRequired(), EqualTo('password')])
    target_calories = FloatField('Daily target calories:', validators=[DataRequired()])
    target_protein = FloatField('Daily target protein:', validators=[DataRequired(), NumberRange(min=0.1, message="Cannot be negative")])
    target_fat = FloatField('Daily target fat:', validators=[DataRequired(), NumberRange(min=0.1, message="Cannot be negative")])
    submit = SubmitField('Register')
    

class EditInfo(FlaskForm):
    target_calories = FloatField('Daily target calories:', validators=[DataRequired()])
    target_protein = FloatField('Daily target protein:', validators=[DataRequired(), NumberRange(min=0.1, message="Cannot be negative")])
    target_fat = FloatField('Daily target fat:', validators=[DataRequired(), NumberRange(min=0.1, message="Cannot be negative")])
    submit = SubmitField('Update')


    def validate_target_calories(self, field):
        min_cal = (self.target_protein.data*4) + (self.target_fat.data*9)
        if field.data < min_cal:
            raise ValidationError(
                "Calories cannot be lower than the macros given."
                )
    
    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user:
            raise ValidationError('Username already taken. Please enter a different username.')
        
class ServingForm(FlaskForm):
    servings = FloatField('Servings:', validators=[DataRequired(), NumberRange(min=0.01, message="Cannot be negative or zero")])
    calories = FloatField('Calories per serving:', validators=[DataRequired(), NumberRange(min=0.01, message="Cannot be negative or zero")])
    protein = FloatField('Protein per serving:', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative or zero")])
    fat = FloatField('Fat per serving:', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative or zero")])
    add = SubmitField('Add')

class WeightForm(FlaskForm):
    weight = FloatField('Weight:', validators=[DataRequired(), NumberRange(min=0.01, message="Cannot be negative or zero")])
    weight_servings = FloatField('Weight per serving:', validators=[DataRequired(), NumberRange(min=0.01, message="Cannot be negative or zero")])
    calories = FloatField('Calories per serving:', validators=[DataRequired(), NumberRange(min=0.01, message="Cannot be negative or zero")])
    protein = FloatField('Protein per serving:', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative or zero")])
    fat = FloatField('Fat per serving:', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative or zero")])
    add = SubmitField('Add')

class QuickAddForm(FlaskForm):
    calories = FloatField('Calories:', validators=[DataRequired(), NumberRange(min=0.01, message="Cannot be negative or zero")])
    protein = FloatField('Protein:', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative or zero")])
    fat = FloatField('Fat:', validators=[InputRequired(), NumberRange(min=0, message="Cannot be negative or zero")])
    add = SubmitField('Add')

class ActionForm(FlaskForm):
    remove = SubmitField('Remove')
    submit = SubmitField('Submit meal')
    new_day = SubmitField("[START NEW DAY]")

