#!/usr/bin/env python3
# coding: utf-8

import dash
from dash import dcc
from flask_login import current_user

dash.register_page(__name__, title="")


def layout():
    if current_user and current_user.is_authenticated:
        return dcc.Location(id="404_login_location", href="/home", refresh=True)
    else:
        return dcc.Location(id="404_logout_location", href="/", refresh=True)
