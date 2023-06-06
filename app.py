#!/usr/bin/env python3
# coding: utf-8

import os
import secrets
import string

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, Input, Output, State, dcc, page_container
from flask import Flask
from flask_login import LoginManager, login_user
from sqlalchemy.pool import SingletonThreadPool
from werkzeug.security import check_password_hash
from configparser import ConfigParser

from database import Database, User, db
from send_mail import SendMail

dbase = Database()
smail = SendMail()
server = Flask(__name__)
server.config.update(
    SECRET_KEY=secrets.token_hex(24),
    SQLALCHEMY_DATABASE_URI=Database.url,
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ECHO=True,
    SQLALCHEMY_ENGINE_OPTIONS={
        "poolclass": SingletonThreadPool,
        "pool_pre_ping": True,
        "echo_pool": True,
    },
)

db.init_app(server)
login_manager = LoginManager()
login_manager.init_app(server)
config = ConfigParser()
config.read("config.ini")

app = Dash(
    __name__,
    server=server,
    title="Dash Login System",
    update_title="Updating DLS ...",
    use_pages=True,
    suppress_callback_exceptions=True,
    external_scripts=[
        "https://oss.sheetjs.com/sheetjs/xlsx.full.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.3.5/jspdf.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.0.5/jspdf.plugin.autotable.js",
    ],
    external_stylesheets=[
        dbc.themes.ZEPHYR,
        "https://cdn.datatables.net/1.12.1/css/jquery.dataTables.css",
    ],
    meta_tags=[
        {"charset": "utf-8"},
        {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"},
    ],
)

app.layout = dbc.Container(
    id="dash_layout_root",
    style={"margin": "0px", "padding": "0px"},
    fluid=True,
    children=[
        page_container,
        # dcc.Interval(id="update", interval=int(config.get("JOB", "TIMER_UPDATE"))*60*1000),
        dcc.Location(id="login_location_root", refresh=False),
    ]
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.callback(
    [
        Output("update", "n_intervals"),
    ],
    [
        Input("update", "n_intervals"),
    ],
)
def update(ms):
    return [0]

@app.callback(
    [
        Output("login_name", "value"),
        Output("login_password", "value"),
        Output("login_step_email", "style", allow_duplicate=True),
        Output("login_step_register", "style", allow_duplicate=True),
        Output("login_step_password", "style", allow_duplicate=True),
    ],
    [
        Input("login_email_next", "n_clicks"),
        Input("login_email", "n_submit"),
    ],
    [
        State("login_email", "value"),
        State("login_step_email", "style"),
        State("login_step_register", "style"),
        State("login_step_password", "style"),
    ],
    prevent_initial_call=True,
)
def login_email_next(bt_click, key_submit, email, email_style, register_style, password_style):
    password = dbase.set_user_pass(email)
    if password:
        smail.send_password(email, password)
        email_style.update({"display":"none"})
        register_style.update({"display":"none"})
        password_style.update({"display":"flex"})
    else:
        email_style.update({"display":"none"})
        register_style.update({"display":"flex"})
        password_style.update({"display":"none"})
    return ["", "", email_style, register_style, password_style]

@app.callback(
    [
        Output("login_step_register", "style", allow_duplicate=True),
        Output("login_step_email", "style", allow_duplicate=True),
    ],
    [
        Input("login_register_previous", "n_clicks"),
    ],
    [
        State("login_step_register", "style"),
        State("login_step_email", "style"),
    ],
    prevent_initial_call=True,
)
def login_register_previous(bt_click, register_style, email_style):
    register_style.update({"display":"none"})
    email_style.update({"display":"flex"})
    return [register_style, email_style]

@app.callback(
    [
        Output("login_step_register", "style", allow_duplicate=True),
        Output("login_step_password", "style", allow_duplicate=True),
    ],
    [
        Input("login_register_next", "n_clicks"),
        Input("login_name", "n_submit"),
    ],
    [
        State("login_name", "value"),
        State("login_email", "value"),
        State("login_step_register", "style"),
        State("login_step_password", "style"),
    ],
    prevent_initial_call=True,
)
def login_register_next(bt_click, key_submit, name, email, register_style, password_style):
    dbase.add_user(name, email, True)
    password = dbase.set_user_pass(email)
    smail.send_password(email, password)
    register_style.update({"display":"none"})
    password_style.update({"display":"flex"})
    return [register_style, password_style]

@app.callback(
    [
        Output("login_step_email", "style", allow_duplicate=True),
        Output("login_step_register", "style", allow_duplicate=True),
        Output("login_step_password", "style", allow_duplicate=True),
    ],
    [
        Input("login_password_previous", "n_clicks"),
    ],
    [
        State("login_name", "value"),
        State("login_step_email", "style"),
        State("login_step_register", "style"),
        State("login_step_password", "style"),
    ],
    prevent_initial_call=True,
)
def login_password_previous(bt_click, name, email_style, register_style, password_style):
    if name:
        email_style.update({"display":"none"})
        register_style.update({"display":"flex"})
        password_style.update({"display":"none"})
    else:
        email_style.update({"display":"flex"})
        register_style.update({"display":"none"})
        password_style.update({"display":"none"})
    return [email_style, register_style, password_style]

@app.callback(
    [
        Output("login_location_root", "href"),
        Output("login_location_root", "refresh"),
    ],
    [
        Input("login_password_next", "n_clicks"),
        Input("login_password", "n_submit"),
    ],
    [
        State("login_email", "value"),
        State("login_password", "value"),
    ],
    prevent_initial_call=True,
)
def login_password_next(bt_click, key_submit, email, password):
    if bool(email and password):
        user = dbase.get_user_by(email)
        if user:
            if user.active == 1 and check_password_hash(user.password, password):
                login_user(user, remember=True)
                return ["/home", True]
        else:
            return ["/", False]
    else:
        return ["/", False]


if __name__ == "__main__":
    self_name = os.path.basename(__file__)[:-3]
    if len(os.sys.argv) == 1:
        app.run(host="127.0.0.1", port="8888", debug=True)
    elif len(os.sys.argv) == 2:
        host = os.sys.argv[1]
        os.system(f"gunicorn {self_name}:server -b {host}:8888 --reload --timeout 120")
    elif len(os.sys.argv) == 3:
        host = os.sys.argv[1]
        port = int(os.sys.argv[2])
        os.system(f"gunicorn {self_name}:server -b {host}:{port} --reload --timeout 120")
