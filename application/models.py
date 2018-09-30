# -*- coding: utf-8 -*-
"""
Created on '2018/8/21 0021'

@author: hszzjs

E-mail: hushaozhe@stu.xidian.edu.cn
"""

import random
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

from application.__init__ import database,login_manager


class User(database.Model):
	id=database.Column(database.Integer,primary_key=True,unique=True,autoincrement=True)
	user_name=database.Column(database.String(30),unique=True)
	head_url=database.Column(database.String(300))
	password=database.Column(database.String(80),unique=True)
	images=database.relationship('Image',backref='user',lazy='dynamic')
	salt=database.Column(database.String(32))
	confirmed=database.Column(database.Boolean,nullable=False,default=False)
	email=database.Column(database.String(50),unique=True,nullable=False)
	
	def __init__(self,user_name,password,salt='', email=''):
		self.user_name=user_name
		self.password=password
		self.head_url=str(random.randint(1,6))+'.jpg'
		self.salt=salt
		self.email=email
	
	def __repr__(self):
		return '<User: %d %s>'%(self.id,self.user_name)
	
	def generate_comfirmation_token(self,expiration=3600):
		s=Serializer(current_app.config['SECRET_KEY'],expiration)
		return s.dumps({'confirm':self.id})
	
	def confirm(self,token):
		s=Serializer(current_app.config['SECRET_KEY'])
		try:
			data=s.loads(token)
		except:
			return False
		if data.get('confirm')!=self.id:
			return False
		self.confirmed=True
		database.session.add(self)
		database.session.commit()
		return True
	
	@property
	def is_authenticated(self):
		return True
	
	@property
	def is_active(self):
	    return  True
	
	@property
	def  is_anonymous(self):
		return False
	
	def get_id(self):
		return self.id

class Image(database.Model):
	id=database.Column(database.Integer,primary_key=True,unique=True,autoincrement=True)
	image=database.Column(database.String(300))
	user_id=database.Column(database.Integer,database.ForeignKey('user.id'))
	created_time=database.Column(database.DateTime)
	comments=database.relationship('Comment')
	
	def __init__(self,image,user_id):
		self.image=image
		self.user_id=user_id
		self.created_time=datetime.now()
	
	def __repr__(self):
		return '<Image: %s %d>'%(self.image,self.user_id)

class Comment(database.Model):
	id=database.Column(database.Integer,primary_key=True,unique=True,autoincrement=True)
	content=database.Column(database.String(300))
	image_id=database.Column(database.Integer,database.ForeignKey('image.id'))
	user_id=database.Column(database.Integer,database.ForeignKey('user.id'))
	status = database.Column(database.Integer, default=0)  # 0正常，1被删除
	user=database.relationship('User')
	
	def __init__(self,content,image_id,user_id):
		self.content=content
		self.image_id=image_id
		self.user_id=user_id
	
	def __repr__(self):
		return '<Comment: %d %s>'%(self.id,self.content)

@login_manager.user_loader
def user_loader(user_id):#注意这里是通过user_id返回到User里面对应id的用户信息，所以使用数据库查询
	return User.query.get(user_id)