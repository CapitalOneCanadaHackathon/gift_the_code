from flask_wtf import Form
from wtforms import IntegerField, TextAreaField, StringField, FloatField, DateField, SelectField
from wtforms.validators import DataRequired


class QueryForm(Form):
    acct_id = IntegerField('Account No')
