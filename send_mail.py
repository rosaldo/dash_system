#!/usr/bin/env python3
# coding: utf-8

import smtplib
from email.message import EmailMessage
from configparser import ConfigParser


class SendMail:
    def __init__(self):
        config = ConfigParser()
        config.read("config.ini")
        self.__smtp_host = config.get("SMTP", "HOST")
        self.__smtp_port = config.get("SMTP", "PORT")
        self.__smtp_user = config.get("SMTP", "USER")
        self.__smtp_pass = config.get("SMTP", "PASS")

    def send_password(self, email, password):
        msg = EmailMessage()
        msg["Subject"] = "Acesso DLS"
        msg["From"] = self.__smtp_user
        msg["To"] = email
        msg.set_content(f"E-mail automático com a senha de acesso ao Dash Login System.\n\n{password}")
        try:
            smtp_server = smtplib.SMTP_SSL(self.__smtp_host, self.__smtp_port)
            smtp_server.login(self.__smtp_user, self.__smtp_pass)
            smtp_server.send_message(msg)
            return True
        except Exception:
            return False
