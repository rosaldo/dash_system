#!/usr/bin/env python3
# coding: utf-8


import dash_bootstrap_components as dbc


def navbar(current_user_name = None):
    return dbc.NavbarSimple(
        id="navbar_home",
        fluid=True,
        links_left=True,
        style={"color":"#777", "font-weight":"bold"},
        children=[
            dbc.DropdownMenu(
                id="menu_login",
                nav=True,
                in_navbar=True,
                label=current_user_name,
                children=[
                    dbc.DropdownMenuItem(
                        "SAIR",
                        href="/logout",
                        style={"color":"#777"},
                    ),
                ],
            ),
        ]
    )
