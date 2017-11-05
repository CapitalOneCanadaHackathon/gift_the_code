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


PROGRAM_SUMMARY = {"attendance_by_program":
                   """SELECT event_name, round(sum((1400 - ( current_date - event_dt)) * 20.00 /1400))::int as attendee_count FROM events
                    WHERE program_ind=1 GROUP BY 1 ORDER BY attendee_count desc
                    """,
                   "funding_by_program":
                   """
                    SELECT program_funded, SUM(donation_amount)/1000 as donations FROM 
                    donations WHERE program_ind=1 GROUP BY 1 ORDER BY donations desc
                    """}

PROGRAMS_ = {"attendance_by_program":
             """SELECT event_name, round(sum((1400 - ( current_date - event_dt)) * 20.00 /1400))::int as attendee_count FROM events
                WHERE program_ind=1 and event_name = '{program}'
                GROUP BY 1 ORDER BY attendee_count desc
                """,
             "funding_by_program":
             """
                SELECT program_funded, SUM(donation_amount) as donations FROM 
                donations WHERE program_ind=1 and program_funded = '{program}'
                GROUP BY 1 ORDER BY donations desc
                """,
             "time_series":
             """
                select a.event_name, b.month, attendance, donations from
                (SELECT event_name,SUBSTRING(event_dt::varchar,1,7) as month, round(sum((1400 - ( current_date - event_dt)) * 20.00 /1400))::int as attendance FROM events
                WHERE program_ind=1 and event_name = '{program}'
                GROUP BY 1,2) a join 
                (SELECT program_funded,SUBSTRING(donation_date::varchar,1,7) as month, SUM(donation_amount) donations FROM donations
                WHERE program_ind=1 and program_funded = '{program}'
                GROUP BY 1,2) b on a.event_name = b.program_funded and a.month = b.month
                """}

EVENTS = {"top_five_evts":
          """
            SELECT event_name, round(sum((1400 - ( current_date - event_dt)) * 20.00 /1400))::int as attendee_count FROM events
            WHERE program_ind = 0 and event_dt between '{dt_start}' and '{dt_end}' GROUP BY 1
            ORDER BY attendee_count DESC LIMIT 6
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
    form = QueryForm(request.form)
    return render_template("programs.html", title="Programs", form=form)


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
    program = request.args.get('program', 'Housing')
    cxn = pg_connect()
    output = dict(data={k: cxn.query_dict(v.format(program=program))
                        for k, v in PROGRAMS_.items()})
    cxn.close()

    return dumps(output)


@app.route('/program_summary_api')
def program_summary_api():
    cxn = pg_connect()
    output = dict(data={k: cxn.query_dict(v)
                        for k, v in PROGRAM_SUMMARY.items()})
    cxn.close()

    return dumps(output)


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
