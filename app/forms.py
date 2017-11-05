from flask_wtf import Form
from wtforms import IntegerField, TextAreaField, StringField, FloatField, DateField, SelectField
from wtforms.validators import DataRequired


class QueryForm(Form):
    program = SelectField('Program', choices=[('Housing', 'Housing'),
                                              ('Family Resource Centre',
                                               'Family Resource Centre'),
                                              ('Meal Trans', 'Meal Trans'),
                                              ('Trans Youth Mentorship',
                                               'Trans Youth Mentorship'),
                                              ('Sunday Drop In', 'Sunday Drop In'),
                                              ('Legal Clinic', 'Legal Clinic'),
                                              ('New Comer Settlement Services', 'New Comer Settlement Services')])
