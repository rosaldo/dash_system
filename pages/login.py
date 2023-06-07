#!/usr/bin/env python3
# coding: utf-8


import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from flask_login import current_user

dash.register_page(__name__, path="/", title="DLS - Login")

def layout():
    if not (current_user and current_user.is_authenticated):
        return dbc.Container(
            fluid=True,
            children=[
                dbc.Row(
                    align="center",
                    justify="center",
                    style={"height":"20cqmax"},
                    children=dbc.Col(
                        style={"text-align":"center"},
                        children=html.H1([html.I("dash "), html.B("Login "), html.Code("SYSTEM")])
                    ),
                ),
                dbc.Row(
                    align="center",
                    justify="center",
                    children=[
                        dcc.Store("login_step_status", storage_type="session"),
                        dbc.Card(
                            id="login_step_email",
                            style={"display":"none"},
                            children=[
                                dbc.CardHeader(
                                    style={"text-align":"center"},
                                    children=html.H3("Login"),
                                ),
                                dbc.CardBody(
                                    children=[
                                        dbc.InputGroup(
                                            style={"margin-bottom":"15px"},
                                            children=[
                                                dbc.InputGroupText("e-mail"),
                                                dbc.Input(
                                                    id="login_email",
                                                    autofocus=True,
                                                    inputmode="email",
                                                    persistence=True,
                                                    persistence_type="session",
                                                    placeholder="digite seu e-mail de login",
                                                    type="text",
                                                )
                                            ]
                                        ),
                                        dbc.Row(
                                            justify="end",
                                            children=[
                                                dbc.Button(
                                                    id="login_email_next",
                                                    style={"width":"90px", "margin-right":"5px"},
                                                    children="próximo",
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        dbc.Card(
                            id="login_step_register",
                            style={"display":"none"},
                            children=[
                                dbc.CardHeader(
                                    style={"text-align":"center"},
                                    children=html.H3("Cadastro"),
                                ),
                                dbc.CardBody(
                                    children=[
                                        dbc.InputGroup(
                                            style={"margin-bottom":"15px"},
                                            children=[
                                                dbc.InputGroupText("nome"),
                                                dbc.Input(
                                                    id="login_name",
                                                    autofocus=True,
                                                    persistence=True,
                                                    persistence_type="session",
                                                    placeholder="digite seu nome",
                                                    type="text",
                                                )
                                            ]
                                        ),
                                        dbc.Row(
                                            justify="between",
                                            children=[
                                                dbc.Button(
                                                    id="login_register_previous",
                                                    style={"width":"90px", "margin-left":"5px"},
                                                    children="anterior",
                                                ),
                                                dbc.Button(
                                                    id="login_register_next",
                                                    style={"width":"90px", "margin-right":"5px"},
                                                    children="próximo",
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        dbc.Card(
                            id="login_step_password",
                            style={"display":"none"},
                            children=[
                                dbc.CardHeader(
                                    style={"text-align":"center"},
                                    children=html.H3("Senha"),
                                ),
                                dbc.CardBody(
                                    children=[
                                        dbc.InputGroup(
                                            style={"margin-bottom":"15px"},
                                            children=[
                                                dbc.InputGroupText("senha"),
                                                dbc.Input(
                                                    id="login_password",
                                                    autofocus=True,
                                                    inputmode="password",
                                                    persistence=True,
                                                    persistence_type="session",
                                                    placeholder="digite a senha que recebeu",
                                                    type="password",
                                                )
                                            ]
                                        ),
                                        dbc.Row(
                                            justify="between",
                                            children=[
                                                dbc.Button(
                                                    id="login_password_previous",
                                                    style={"width":"90px", "margin-left":"5px"},
                                                    children="anterior",
                                                ),
                                                dbc.Button(
                                                    id="login_password_next",
                                                    style={"width":"90px", "margin-right":"5px"},
                                                    children="próximo",
                                                )
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                    ]
                )
            ],
        )
    else:
        return dcc.Location(id="login_location_login", href="/home", refresh=True)
