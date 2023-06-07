#!/usr/bin/env python3
# coding: utf-8

import os
import secrets
import string

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, dcc, html, page_container
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
        dbc.themes.SPACELAB,
        "https://cdn.datatables.net/1.12.1/css/jquery.dataTables.css",
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css",
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
        Output("login_step_email", "style", allow_duplicate=True),
        Output("login_step_register", "style", allow_duplicate=True),
        Output("login_step_password", "style", allow_duplicate=True),
        Output("login_step_status", "data", allow_duplicate=True),
    ],
    [
        Input("login_step_status", "data"),
    ],
    prevent_initial_call="initial_duplicate",
)
def set_status_login(data):
    if not data:
        data = {
            "email":{"width":"400px","padding":"0px","display":"flex"},
            "register":{"width":"400px","padding":"0px","display":"none"},
            "password":{"width":"400px","padding":"0px","display":"none"},
        }
    email = data["email"]
    register = data["register"]
    password = data["password"]
    return [email, register, password, data]

@app.callback(
    [
        Output("login_name", "value"),
        Output("login_password", "value"),
        Output("login_step_status", "data", allow_duplicate=True),
    ],
    [
        Input("login_email_next", "n_clicks"),
        Input("login_email", "n_submit"),
    ],
    [
        State("login_email", "value"),
        State("login_step_status", "data"),
    ],
    prevent_initial_call=True,
)
def login_email_next(bt_click, key_submit, email, data):
    if email:
        password = dbase.set_user_pass(email)
        if password:
            smail.send_password(email, password)
            data["email"].update({"display":"none"})
            data["register"].update({"display":"none"})
            data["password"].update({"display":"flex"})
        else:
            data["email"].update({"display":"none"})
            data["register"].update({"display":"flex"})
            data["password"].update({"display":"none"})
    return ["", "", data]

@app.callback(
    [
        Output("login_step_status", "data", allow_duplicate=True),
    ],
    [
        Input("login_register_previous", "n_clicks"),
    ],
    [
        State("login_step_status", "data"),
    ],
    prevent_initial_call=True,
)
def login_register_previous(bt_click, data):
    data["register"].update({"display":"none"})
    data["email"].update({"display":"flex"})
    return [data]

@app.callback(
    [
        Output("login_step_status", "data", allow_duplicate=True),
    ],
    [
        Input("login_register_next", "n_clicks"),
        Input("login_name", "n_submit"),
    ],
    [
        State("login_name", "value"),
        State("login_email", "value"),
        State("login_step_status", "data"),
    ],
    prevent_initial_call=True,
)
def login_register_next(bt_click, key_submit, name, email, data):
    if name:
        dbase.add_user(name, email, True)
        password = dbase.set_user_pass(email)
        smail.send_password(email, password)
        data["register"].update({"display":"none"})
        data["password"].update({"display":"flex"})
    return [data]

@app.callback(
    [
        Output("login_step_status", "data", allow_duplicate=True),
    ],
    [
        Input("login_password_previous", "n_clicks"),
    ],
    [
        State("login_name", "value"),
        State("login_step_status", "data"),
    ],
    prevent_initial_call=True,
)
def login_password_previous(bt_click, name, data):
    if name:
        data["email"].update({"display":"none"})
        data["register"].update({"display":"flex"})
        data["password"].update({"display":"none"})
    else:
        data["email"].update({"display":"flex"})
        data["register"].update({"display":"none"})
        data["password"].update({"display":"none"})
    return [data]

@app.callback(
    [
        Output("login_password", "type"),
        Output("login_password_toggle", "children"),
    ],
    [
        Input("login_password_toggle", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def toggle_password_visibility(bt_click):
    if bt_click % 2 == 1:
        return ["text", html.I(className="bi bi-eye-fill")]
    else:
        return ["password", html.I(className="bi bi-eye-slash-fill")]


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
    if email and password:
        user = dbase.get_user_by(email)
        if user:
            if user.active == 1 and check_password_hash(user.password, password):
                login_user(user, remember=True)
                return ["/home", True]
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
