# -*- coding: utf-8 -*-
"""
Created on '2018/8/21 0021'

@author: hszzjs

E-mail: hushaozhe@stu.xidian.edu.cn
"""
from flask_login._compat import unicode

from application.__init__ import app, database
from flask import render_template, redirect,request,flash,get_flashed_messages,url_for,send_from_directory
import random,hashlib,json,uuid,os
from application.models import User, Image,Comment
from flask_login import login_user,logout_user,login_required,current_user
from application.email import send_email
from application.qiniusdk import save_file_to_cloud
from application.reglogin.forms import LoginForm,RegisterForm



@app.route('/')
def index():
	images=Image.query.order_by(database.desc(Image.id)).all()
	return render_template('index.html',images=images)

#首页ajax的json数据
@app.route('/images/<int:page_num>/<int:per_page>')
def index_paginate(page_num,per_page):
	images=Image.query.order_by('id desc').paginate(page=page_num,per_page=per_page,error_out=False)
	map={'has_next':images.has_next}
	image=[]
	for item in images.items:
		comment_user_username=[]
		comment_user_id=[]
		comment_content=[]
		for comment_i in item.comments:
			comment_user_username.append(comment_i.user.user_name)
			comment_user_id.append(comment_i.user.id)
			comment_content.append(comment_i.content)
		
		imgov={'image_user_id':item.user.id,'image_user_head_url':item.user.head_url,'image_user_username':item.user.user_name,'image_id':item.id,
		       'image_url':item.id,'image_url':item.url,'image_comments_length':len(item.comments),'comment_user_username':comment_user_username,
		       'comment_user_id':comment_user_id,'comment_content':comment_content}
		image.append(imgov)
	map['images']=image
	return json.dumps(map)

@app.route('/image/<int:image_id>')
def image(image_id):
	image=Image.query.get(image_id)
	if image==None:
		return redirect('/')
	return render_template('pageDetail.html',image=image)

#个人详情页
@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
	user=User.query.get(user_id)
	if user==None:
		return redirect('/')
	return render_template('profile.html',user=user)

#个人详情页 ajax数据
@app.route('/profile/images/<int:id>/<int:page_num>/<int:per_page>/')
@login_required
def profile_paginate(id,page_num,per_page):
	user=User.query.get(id)
	paginate=user.images.paginate(page=page_num,per_page=per_page,error_out=False)
	map={'has_next':paginate.has_next}
	images=[]
	for image in paginate.items:
		imgvo={'id':image.id,'url':image.image}
		images.append(imgvo)
	map['images']=images
	return json.dumps(map)

@app.route('/regloginpage/')
def regloginpage():
	msg=''
	for m in get_flashed_messages(with_categories=False,category_filter=['reglogin']):
		msg=msg+m
	return render_template('login.html',msg=msg,next=request.values.get('next'))

def redirect_with_msg(target,msg,catergory):
	if msg!=None:
		flash(msg,category=catergory)
	return redirect(target)

@app.route('/login/',methods={'get','post'})
def login():
	user_name=request.values.get('user_name').strip()
	password=request.values.get('password').strip()
	
	if user_name=='' or password=='':
		return redirect_with_msg('/regloginpage/',u'用户名或密码不能为空','reglogin')
	
	user=User.query.filter_by(user_name=user_name).first()
	if user==None:
		return redirect_with_msg('/regloginpage/',u'用户名不存在','reglogin')
	m=hashlib.md5()
	m.update((password+user.salt).encode('utf8'))
	if (m.hexdigest()!=user.password):
		return redirect_with_msg('regloginpage',u'密码错误','reglogin')
	login_user(user)
	
	next = request.values.get('next')
	if next != None and next.startswith('/'):
		return redirect(next)
	return redirect('/')

#注册
@app.route('/reg/',methods={'post','get'})
def reg():
	user_name=request.values.get('user_name').strip()
	password=request.values.get('password').strip()
	
	if user_name=="" or password=="":
		return redirect_with_msg('/regloginpage/',u'用户名或密码不能为空','reglogin')
	
	user=User.query.filter_by(user_name=user_name).first()
	if user!=None:
		return redirect_with_msg('/regloginpage/',u'用户名已存在','reglogin')
	
	salt='.'.join(random.sample('hwerfuaihvfYUGIUVGUYERWSYRTwuieyhf9iwof85674913987',10))
	m=hashlib.md5()
	m.update((password+salt).encode("utf8"))
	password=m.hexdigest()
	user=User(user_name,password,salt)
	database.session.add(user)
	database.session.commit()
	
	#注册完毕后自动登录
	login_user(user)
	
	next=request.values.get('next')
	if next!=None and next.startswith('/'):
		return redirect(next)
	return redirect('/')

@app.route('/logout/')
def logout():
	logout_user()
	return redirect('/')

#以上都是旧版的登录注册，下面的新的需要进行email验证的登录注册
@app.route('/wtf/reg/',methods=['GET','POST'])
def wtf_reg():
	form=RegisterForm()
	if form.validate_on_submit():
		salt='.'.join(random.sample('hbuwgcfwijFTYURUYBufyou16871234967',10))
		password=form.password.data
		m=hashlib.md5()
		m.update((password+salt).encode('utf8'))
		password=m.hexdigest()
		user=User(form.user_name.data,password,salt,form.email.data)
		database.session.add(user)
		database.session.commit()
		
		token=user.generate_comfirmation_token()
		send_email(form.email.data,u'Please activte your account',u'mail/new_user',user=user,token=token)
		
		login_user(user)
		next=request.args.get('next')
		if next!=None:
			return  redirect(next)
		return redirect('/profile/'+unicode(user.id))
	return render_template('reglogin/reglogin_register.html',form=form)

@app.route('/wtf/login/',methods=['get','post'])
def wtf_login():
	form=LoginForm()
	if form.validate_on_submit():
		user=User.query.filter_by(user_name=form.user_name.data).first()
		if user is not None:
			m=hashlib.md5()
			m.update((form.password.data+user.salt).encode('utf8'))
			password=m.hexdigest()
			
			if password!=user.password:
				return redirect_with_msg('/wtf/login/',u'密码不正确','login')
			login_user(user)
			
			next=request.args.get('next')
			if next!=None:
				return redirect(next)
			return redirect('/profile/'+user.id)
		flash('用户不存在')
	return render_template('reglogin/reglogin_login.html',form=form)

@app.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.conformed:
		return redirect('/')
	if current_user.confirm(token):
		flash('您的账户已被激活')
	else:
		flash('您的账户尚未被激活')
	return redirect('/')

def save_to_local(file,file_name):
	save_dir=app.config['UPLOAD_DIR']
	file.save(os.path.join(save_dir,file_name))
	return file_name

@app.route('/upload/',methods={'post'})
@login_required
def upload():
	file=request.files['file']
	file_ext=''
	if file.filename.find('.')>0:
		file_ext=file.filename.rsplit('.',1)[1].strip().lower()
	if file_ext in app.config['ALLOWED_EXT']:
		file_name=str(uuid.uuid1()).replace('-','')+'.'+file_ext
		url=save_to_local(file,file_name)
		if url!=None:
			database.session.add(Image(url,current_user.id))
			database.session.commit()
	return redirect('/profile/%d'%current_user.id)

@app.route('/addcomment/',methods={'post'})
def add_comment():
	image_id=int(request.values['image_id'])
	content=request.values['content']
	comment=Comment(content,image_id, current_user.id)
	database.session.add(comment)
	database.session.commit()
	map={"code":0,"id":comment.id,"content":comment.content,"username":comment.user.user_name,"user_id":comment.user_id}
	return json.dumps(map)