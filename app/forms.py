from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models.user import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditUserRoleForm(FlaskForm):
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Update Role')

class CreateCylinderForm(FlaskForm):
    cylinder_id_tag = StringField('Cylinder ID Tag', validators=[DataRequired(), Length(min=3, max=64)])
    submit = SubmitField('Create Cylinder')

    def validate_cylinder_id_tag(self, cylinder_id_tag):
        cylinder = Cylinder.query.filter_by(cylinder_id_tag=cylinder_id_tag.data).first()
        if cylinder is not None:
            raise ValidationError('This Cylinder ID Tag is already registered.')

class UpdateCylinderStatusForm(FlaskForm):
    status = SelectField('New Status', choices=[
        ('created', 'Created'), # Should generally not be set manually after creation
        ('available', 'Available'), # A state after creation or reception, ready for delivery
        ('received', 'Received'), # When a cylinder is returned/received
        ('delivered', 'Delivered'), # When a cylinder is given out
        ('maintenance', 'Maintenance')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')
