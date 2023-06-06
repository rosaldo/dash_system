#!/usr/bin/env python3
# coding: utf-8

import os
import secrets
import string

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    active = db.Column(db.Boolean)

class Database:
    __script_name = os.path.basename(__file__)[:-3]
    __script_path = os.path.dirname(os.path.realpath(__file__))
    url = f"sqlite:///{__script_path}{os.sep}{__script_name}.sql3"
    
    def __init__(self):
        self.engine = create_engine(
            self.url,
            poolclass=SingletonThreadPool,
            pool_pre_ping=True,
            echo_pool=True,
            echo=True,
        )
        self.session = sessionmaker(bind=self.engine)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        if "user" not in self.metadata.tables:
            User.__table__.create(self.engine)
    
    def add_user(self, name, email, active):
        new_user = User(
            name=name,
            email=email,
            active=active
        )
        try:
            session = self.session()
            session.add(new_user)
            session.commit()
            session.close()
            return True
        except Exception:
            session.rollback()
            return False
    
    def get_user_by(self, email):
        session = self.session()
        user = session.query(User).filter(User.email == email)
        session.close()
        if bool(user.count()):
            return user[0]
        else:
            return False
    
    def set_user_pass(self, email):
        password_size = 21
        digits = string.ascii_letters + string.digits # + string.punctuation
        password = "".join(secrets.choice(digits) for _ in range(password_size))
        session = self.session()
        user = session.query(User).filter(User.email == email)
        if bool(user.count()):
            user[0].password = generate_password_hash(password)
            session.commit()
            session.close()
            return password
        else:
            return False
