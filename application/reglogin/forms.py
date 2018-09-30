# -*- coding: utf-8 -*-
"""
Created on '2018/9/2 0002'

@author: hszzjs

E-mail: hushaozhe@stu.xidian.edu.cn
"""
from flask_wtf import Form
from wtforms import StringField,PasswordField,SubmitField,ValidationError
from wtforms.validators import Required,Length,Email,EqualTo
from application.models import User

class LoginForm(Form):
	user_name=StringField(u'用户名',validators=[Required(),Length(1,32)])
	password=PasswordField(u'密码',validators=[Required()])
	submit=SubmitField(u'登录')

class RegisterForm(Form):
	email=StringField(u'邮箱',validators=[Required(),Length(1,64),Email()])
	user_name=StringField(u'用户名',validators=[Required(),Length(1,32)])
	password=PasswordField(u'密码',validators=[Required()])
	password_confirm=PasswordField(u'确认密码',validators=[Required(),EqualTo('password',u'密码不一致')])
	submit=SubmitField(u'注册')
	
	def validate_username(self,field):
		if User.query.filter_by(user_name=field.data).first():
			raise ValidationError('用户名已存在')
	
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('该邮箱已经被注册')