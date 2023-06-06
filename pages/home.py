#!/usr/bin/env python3
# coding: utf-8

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from flask_login import current_user

# from pages.menu_bar import navbar

dash.register_page(__name__, path_template="/home", title="DLS - Home")

def layout():
    if current_user and current_user.is_authenticated:
        return dbc.Container(
            fluid=True,
            style={"margin": "0px", "padding": "0px"},
            children=[],
        )
    else:
        return dcc.Location(id="home_location_logout", href="/", refresh=True)
