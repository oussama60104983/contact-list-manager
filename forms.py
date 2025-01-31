from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FileField
from wtforms.validators import DataRequired

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email')
    type = SelectField('Type', 
                      choices=[('Personal', 'Personal'), 
                               ('Work', 'Work'),
                               ('Family', 'Family'),
                               ('Friend', 'Friend'),
                               ('Emergency', 'Emergency'),
                               ('Other', 'Other')],
                      validators=[DataRequired()])
    custom_type = StringField('Specify Type')
    image = FileField('Photo')
    submit = SubmitField('Submit')
