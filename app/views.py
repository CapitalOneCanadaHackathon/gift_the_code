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
from .database_operations import pg_connect
# from .models import Account
# from .utils import *

# begin user access management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
# login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(eid):
    return Account.get(eid)


def get_from_database(metrics, dt_start='2010-01-01', dt_end='2099-01-01'):
    cxn = pg_connect()
    output = dict(data={k: cxn.query_dict(v.format(dt_start=dt_start,
                                                   dt_end=dt_end)) for k, v in metrics.items()})
    cxn.close()
    return output

SUMMARY = {"ttl_donation": "SELECT sum(donation_amount) donation_amt FROM donations WHERE donor_type='Individual' and donation_date between '{dt_start}' and '{dt_end}'",
           "ttl_funding": "SELECT sum(donation_amount) funding_amt FROM donations WHERE donor_type='Organization' and donation_date between '{dt_start}' and '{dt_end}'",
           "evts": "select count(*) from events where event_dt between '{dt_start}' and '{dt_end}'"}

PROGRAMS = {"attendance_by_program":
            """SELECT event_name, COUNT(*) as attendee_count FROM events
                WHERE program_ind = 1 and event_dt between '{dt_start}' and '{dt_end}'
                GROUP BY 1 ORDER BY attendee_count desc
                """,
            "funding_by_program":
                """
                SELECT program_funded, SUM(donation_amount) as donations FROM 
                donations WHERE program_ind=1 and event_dt between '{dt_start}' and '{dt_end}'
                GROUP BY 1 ORDER BY donations desc
                """,
            "attendance_time_series":
                """
                SELECT event_name,SUBSTRING(event_dt,1,7) as month, COUNT(*) as attendance FROM events
                WHERE program_ind=1-- and event_dt between '{dt_start}' and '{dt_end}'
                GROUP BY 1,2 ORDER BY 1 asc,2 asc
                """,
            "funding_time_series":
                """
                SELECT program_funded,SUBSTRING(donation_date,1,7) as month, SUM(donation_amount) FROM donations
                WHERE program_ind=1 and event_dt between '{dt_start}' and '{dt_end}'
                GROUP BY 1,2 ORDER BY 1 asc,2 asc
                """}


@app.route("/")
@app.route("/index", methods=["GET", "POST"])
def index():
    metrics = get_from_database(SUMMARY)
    return render_template("index.html",
                           metrics=dumps(metrics))


@app.route("/summary_api")
def summary_api():
    metrics = get_from_database(PROGRAMS)
    return dumps(metrics)


@app.route("/programs")
def programs():
    return


@app.route("/events")
def events():
    return


@app.route("/members")
def members():
    return


@app.route("/donations")
def donations():
    return


@app.route("/program_api")
def program_api():
    dt_start = request.get("dt_start")
    dt_end = request.get("dt_end")

    return


@app.route("/event_api")
def event_api():
    dt_start = request.get("dt_start")
    dt_end = request.get("dt_end")

    return


@app.route("/member_api")
def member_api():
    dt_start = request.get("dt_start")
    dt_end = request.get("dt_end")

    return


@app.route("/donation_api")
def donation_api():
    dt_start = request.get("dt_start")
    dt_end = request.get("dt_end")

    return


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        sheet = request.get_sheet(field_name="file")
        print(sheet)
        return render_template("index.html")


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     next = request.args.get("next")

#     # app.logger.debug("Arrived at login page... Next: %s" %(next))
#     if current_user is not None and current_user.is_authenticated:
#         app.logger.info("Already logged in, redirecting to home page")
#         return redirect(url_for("index"))

#     elif request.method == "POST":
#         # validate username and password
#         eid = request.form["eid"].lower()
#         app.logger.info("Attempting to log in %s... Next: %s" % (eid, next))

#         # create the user via ldap
#         account = Account.get_via_ldap(eid, request.form["pwd"])
#         if(account):
#             groups = "|".join(account.groups(eid))
#             if "IRIS" in groups or "PHDP" in groups:
#                 app.logger.info("Logging in %s..." % (eid))
#                 login_user(account)
#                 # Tell Flask-Principal the identity changed
#                 identity_changed.send(app, identity=Identity(account.id))

#                 app.logger.debug("Is %s authenticated? %s" %
#                                  (eid, account.is_authenticated()))
#                 app.logger.info("Logged in successfully")

#                 # next_is_valid should check if the user has valid
#                 # permission to access the `next` url
#                 if not next_is_valid(next):
#                     return abort(400)

#                 return redirect(next or url_for("index"))
#             else:
#                 app.logger.warning(
#                     "Could not log in %s. Invalid AD groups!" % (eid)
#                 )
#                 flash("Invalid credentials, please apply for IRIS access", "danger")
#         else:
#             app.logger.warning(
#                 "Could not log in %s. Invalid credentials!" % (eid))
#             flash("Invalid username or password.", "danger")

#     return render_template("login.html")


# @app.route("/logout")
# def logout():
#     app.logger.info("Attempting to log out...")
#     eid = current_user.id
#     logout_user()
#     app.logger.info("Logged out %s successfully" % (eid))
#     flash("Logged out successfully.", "success")
#     return redirect(url_for("login"))
