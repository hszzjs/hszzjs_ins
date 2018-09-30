# -*- coding: utf-8 -*-
"""
Created on '2018/9/1 0001'

@author: hszzjs

E-mail: hushaozhe@stu.xidian.edu.cn
"""
from flask import  render_template
from flask_mail import  Message
from application import app,mail

def send_email(to,subject,template,**kwargs):
	msg=Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject, sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
	msg.body=render_template(template+'.txt',**kwargs)
	msg.html=render_template(template+'.html',**kwargs)
	mail.send(msg)