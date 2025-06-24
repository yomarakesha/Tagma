from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, DateField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email

class Step1Form(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    company_name = StringField('Company Name')
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone number', validators=[DataRequired()])
    subject = StringField('Subject')
    message = TextAreaField('Text message', validators=[DataRequired()])

class Step2Form(FlaskForm):
    meeting_date = StringField('Meeting Date', validators=[DataRequired()])
    meeting_time = StringField('Meeting Time', validators=[DataRequired()])
    timezone = StringField('Timezone', validators=[DataRequired()])

class Step3Form(FlaskForm):
    terms_accepted = BooleanField('Accept Terms', validators=[DataRequired()])
    # Можно добавить скрытое поле для передачи id заявки
    request_id = HiddenField('Request ID')