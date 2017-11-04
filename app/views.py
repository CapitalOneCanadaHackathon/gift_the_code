from __future__ import division, print_function

import datetime
from json import dumps
import re
import os

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, current_user,
                         login_required, login_user, logout_user)

from app import app

import flask_excel as excel

from .forms import QueryForm
# from .models import Account
# from .utils import *

# begin user access management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(eid):
    return Account.get(eid)


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
  if request.method == 'POST':
    sheet = request.get_sheet(field_name='file')
    print(sheet)
    return render_template('index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     next = request.args.get('next')

#     # app.logger.debug('Arrived at login page... Next: %s' %(next))
#     if current_user is not None and current_user.is_authenticated:
#         app.logger.info('Already logged in, redirecting to home page')
#         return redirect(url_for('index'))

#     elif request.method == 'POST':
#         # validate username and password
#         eid = request.form['eid'].lower()
#         app.logger.info('Attempting to log in %s... Next: %s' % (eid, next))

#         # create the user via ldap
#         account = Account.get_via_ldap(eid, request.form['pwd'])
#         if(account):
#             groups = "|".join(account.groups(eid))
#             if 'IRIS' in groups or 'PHDP' in groups:
#                 app.logger.info('Logging in %s...' % (eid))
#                 login_user(account)
#                 # Tell Flask-Principal the identity changed
#                 identity_changed.send(app, identity=Identity(account.id))

#                 app.logger.debug('Is %s authenticated? %s' %
#                                  (eid, account.is_authenticated()))
#                 app.logger.info('Logged in successfully')

#                 # next_is_valid should check if the user has valid
#                 # permission to access the `next` url
#                 if not next_is_valid(next):
#                     return abort(400)

#                 return redirect(next or url_for('index'))
#             else:
#                 app.logger.warning(
#                     'Could not log in %s. Invalid AD groups!' % (eid)
#                 )
#                 flash('Invalid credentials, please apply for IRIS access', 'danger')
#         else:
#             app.logger.warning(
#                 'Could not log in %s. Invalid credentials!' % (eid))
#             flash('Invalid username or password.', 'danger')

#     return render_template('login.html')


# @app.route('/logout')
# def logout():
#     app.logger.info('Attempting to log out...')
#     eid = current_user.id
#     logout_user()
#     app.logger.info('Logged out %s successfully' % (eid))
#     flash('Logged out successfully.', 'success')
#     return redirect(url_for('login'))
