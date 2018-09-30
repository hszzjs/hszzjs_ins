# -*- coding: utf-8 -*-
"""
Created on '2018/8/21 0021'

@author: hszzjs

E-mail: hushaozhe@stu.xidian.edu.cn
"""
import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap

pymysql.install_as_MySQLdb()

app=Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config.from_pyfile('app.conf')
app.secret_key='hszzjs'
database=SQLAlchemy(app)
login_manager=LoginManager(app)
login_manager.login_view='/regloginpage/'
bootstrap=Bootstrap(app)
mail=Mail(app)

from application import views, models