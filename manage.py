# -*- coding: utf-8 -*-
"""
Created on '2018/8/21 0021'

@author: hszzjs

E-mail: hushaozhe@stu.xidian.edu.cn
"""

import random

from application.__init__ import database, app
from flask_script import Manager

from application.models import User, Image, Comment

manager=Manager(app)

@manager.command
def init_database():
	database.drop_all()
	database.create_all()
	for i in range(2):
		database.session.add(User('zyxzjs'+str(i),'lay'+str(i),'','issing'+str(i)+'@163.com'))
		database.session.commit()
	for i in range(3):
		url=str(random.randint(1,6)) + '.jpg'
		database.session.add(Image(url,1))
		for j in range(3):
			database.session.add(Comment('Issing'+str(i)+str(j),1+i*2,2))
		url =str(random.randint(1,6)) + '.jpg'
		database.session.add(Image(url, 2))
		for j in range(3):
			database.session.add(Comment('xback'+str(i)+str(j),(i+1)*2,1))
		database.session.commit()

if __name__=='__main__':
	manager.run()