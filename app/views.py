from __future__ import division, print_function

import datetime
from json import dumps
import re
import os

from itertools import groupby
from operator import itemgetter
from pprint import pprint
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
    output = dict(data={k: cxn.query(v.format(dt_start=dt_start,
                                              dt_end=dt_end)) for k, v in metrics.items()})
    cxn.close()
    return output


def get_from_database_dict(metrics, dt_start='2010-01-01', dt_end='2099-01-01'):
    cxn = pg_connect()
    output = dict(data={k: cxn.query_dict(v.format(dt_start=dt_start,
                                                   dt_end=dt_end)) for k, v in metrics.items()})
    cxn.close()
    return output


def two_axes_chart(data, type):
    x, y = zip(*data)
    return dict(data=[dict(x=x, y=y, type=type)])


def three_axes_chart(data):
    groups = groupby(sorted(data, key=lambda x: x[0]), key=itemgetter(0))
    traces = [{'name': k, 'type': 'scatter',  'mode': 'lines',
               'data': [x[1:] for x in v]} for k, v in groups]
    for trace in traces:
        trace['x'] = [x[0] for x in trace['data']]
        trace['y'] = [x[1] for x in trace['data']]
        del trace['data']
    return traces


SUMMARY = {"ttl_donation": "SELECT sum(donation_amount) donation_amt FROM donations WHERE donor_type='Individual' and donation_date between '{dt_start}' and '{dt_end}'",
           "ttl_funding": "SELECT sum(donation_amount) funding_amt FROM donations WHERE donor_type='Organization' and donation_date between '{dt_start}' and '{dt_end}'",
           "programs": "SELECT round(sum((1400 - ( current_date - event_dt)) * 1.00 /1400))::int as count FROM events WHERE program_ind = 1 and event_dt between '{dt_start}' and '{dt_end}'",
           "donors":
           """
                SELECT member_count + non_member_count as donors from
                (SELECT count(distinct member_id) + 38271 as member_count
                , sum(case when member_id = 999999999 then 1 else 0 end) as non_member_count
                from donations where donor_type = 'Individual' and donation_date between '{dt_start}' and '{dt_end}') a
                """,
           "funders":
           """
                SELECT sum(case when donor_type = 'Organization' then 1 else 0 end) as funder_count
                from donations where donation_date  between '{dt_start}' and '{dt_end}'
                """,
           "evts": "SELECT round(sum((1400 - ( current_date - event_dt)) * 1.00 /1400))::int as count from events where program_ind = 0 and event_dt between '{dt_start}' and '{dt_end}'",
           }


PROGRAMS = {"attendance_by_program":
            """SELECT event_name, COUNT(*) * (1400 - ( current_date - event_dt)) * 1.00 /1400 as attendee_count FROM events
                WHERE program_ind=1 and event_dt between '{dt_start}' and '{dt_end}'
                GROUP BY 1 ORDER BY attendee_count desc
                """,
            "funding_by_program":
                """
                SELECT program_funded, SUM(donation_amount) as donations FROM 
                donations WHERE program_ind=1 and donation_date between '{dt_start}' and '{dt_end}'
                GROUP BY 1 ORDER BY donations desc
                """,
            "attendance_time_series":
                """
                SELECT event_name,SUBSTRING(event_dt::varchar,1,7) as month, COUNT(*) * (1400 - ( current_date - event_dt)) * 1.00 /1400 as attendance FROM events
                WHERE program_ind=1-- and event_dt between '{dt_start}' and '{dt_end}'
                GROUP BY 1,2 ORDER BY 1 asc,2 asc
                """,
            "funding_time_series":
                """
                SELECT program_funded,SUBSTRING(donation_date::varchar,1,7) as month, SUM(donation_amount) FROM donations
                WHERE program_ind=1 and donation_date between '{dt_start}' and '{dt_end}'
                GROUP BY 1,2 ORDER BY 1 asc,2 asc
                """}


PROGRAMS_ = {"attendance_by_program":
             """SELECT event_name, round(sum((1400 - ( current_date - event_dt)) * 1.00 /1400))::int as attendee_count FROM events
                WHERE program_ind=1 and event_dt between '{dt_start}' and '{dt_end}'
                GROUP BY 1 ORDER BY attendee_count desc
                """,
             "funding_by_program":
             """
                SELECT program_funded, SUM(donation_amount) as donations FROM 
                donations WHERE program_ind=1 and donation_date between '{dt_start}' and '{dt_end}'
                GROUP BY 1 ORDER BY donations desc
                """,
             "time_series":
             """
                select a.event_name, b.month, attendance, donations from
                (SELECT event_name,SUBSTRING(event_dt::varchar,1,7) as month, round(sum((1400 - ( current_date - event_dt)) * 1.00 /1400))::int as attendance FROM events
                WHERE program_ind=1
                GROUP BY 1,2) a join 
                (SELECT program_funded,SUBSTRING(donation_date::varchar,1,7) as month, SUM(donation_amount) donations FROM donations
                WHERE program_ind=1
                GROUP BY 1,2) b on a.event_name = b.program_funded and a.month = b.month
                """}

EVENTS = {"top_five_evts":
          """
            SELECT event_name,event_dt::varchar, attendee_count FROM (
            SELECT event_id, event_name,event_dt, COUNT(*) as attendee_count FROM events
            WHERE program_ind = 0 and event_dt between '{dt_start}' and '{dt_end}' GROUP BY 1,2,3
            ) a ORDER BY attendee_count DESC LIMIT 5
            """}

DONATIONS = {"donations_over_time":
             """
                SELECT SUBSTRING(donation_date::varchar,1,7) as month, SUM(donation_amount) FROM donations
                WHERE program_ind=0 and donation_date between '{dt_start}' and '{dt_end}'
                GROUP BY 1 ORDER BY 1 asc
                """}

MEMBERS = {"membership_over_time":
           """
                SELECT SUBSTRING(join_date::varchar,1,7) as month, COUNT(*) FROM members
                GROUP BY 1 ORDER BY 1--{dt_start} {dt_end}
                """,
           "age_of_members":
           """select case when age < 25 then '< 25'
                        when age < 30 then '25 - 29'
                        when age < 35 then '30 - 34'
                        when age < 40 then '35 - 39'
                        else '40 +' end age_range, sum(count) count from
            (SELECT (CURRENT_DATE - birth_date)/365::int as age, COUNT(*)::int count FROM members
                            GROUP BY 1) a group by 1 order by 1--{dt_start} {dt_end}
                """,
           "membership_length":
           """select case 
                    when membership_length > 4 then '0 - 2 years'
                    when membership_length > 3 then '2 - 4 years'
                    when membership_length > 2 then '4 - 6 years'
                    when membership_length > 0 then '6 - 8 years' 
                    else '8+ years' end membership_age_range, count(*) count
            from members group by 1 order by 1;--{dt_start} {dt_end}
            """}


@app.route("/")
@app.route("/index", methods=["GET", "POST"])
def index():
    metrics = get_from_database(SUMMARY)
    return render_template("index.html",
                           metrics=dumps(metrics), title="Overview")


@app.route("/summary_api")
def summary_api():
    metrics = get_from_database(SUMMARY)
    return dumps(metrics)


@app.route("/programs")
def programs():
    return render_template("programs.html", title="Programs")


@app.route("/events")
def events():
    return render_template("events.html", title="Events")


@app.route("/members")
def members():
    return render_template("members.html", title="Members")


@app.route("/donations")
def donations():
    return render_template("donations.html", title="Donations")


@app.route("/program_api")
def program_api():
    # metrics = get_from_database(PROGRAMS)
    # for chart in metrics['data']:
    #     if len(metrics['data'][chart][0]) == 2:
    #         metrics['data'][chart] = two_axes_chart(
    #             metrics['data'][chart], 'bar')

    #     elif len(metrics['data'][chart][0]) == 3:
    #         metrics['data'][chart] = three_axes_chart(
    #             metrics['data'][chart])
    metrics = get_from_database_dict(PROGRAMS_)
    return dumps(metrics)


@app.route("/event_api")
def event_api():
    metrics = get_from_database_dict(EVENTS)
    return dumps(metrics)


@app.route("/member_api")
def member_api():
    metrics = get_from_database_dict(MEMBERS)

    return dumps(metrics)


@app.route("/donation_api")
def donation_api():
    metrics = get_from_database_dict(DONATIONS)
    return dumps(metrics)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    # if request.method == "POST":
    #     sheet = request.get_sheet(field_name="file")
    #     print(sheet)
    #     return render_template("index.html")
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
