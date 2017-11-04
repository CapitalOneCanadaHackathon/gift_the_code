from flask import url_for, flash
from flask_login import logout_user, current_user, UserMixin
import os
import postgrez
from datetime import datetime

from . import app
from .authentication import LDAP
from jinja2 import Environment, FileSystemLoader

import config
import app.utils as utils
from .logger import create_logger


log = create_logger(__name__, log_level='DEBUG')

TEMPLATE_ENVIRONMENT = Environment(
    loader=FileSystemLoader(config.QUERIES_DIR), trim_blocks=True)


class Account(UserMixin):
    ''' extend the UserMixin class
            https://flask-login.readthedocs.org/en/latest/_modules/flask_login.html#UserMixin
    '''

    ldap_session = None

    def __init__(self, eid):
        self.id = eid

    @classmethod
    def get(self, id):
        return self(id)

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
