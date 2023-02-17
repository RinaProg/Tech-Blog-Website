from flask import Flask,request,session,redirect
from flask import render_template
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
import math
import pymysql
pymysql.install_as_MySQLdb()



with open('config.json','r') as c:
    params=json.load(c)["params"]
app=Flask(__name__) 
app.secret_key = "super-secret-key"
app.config['UPLODER_FOLDER'] = params['uploder_location'] 

local_server = True
if (local_server):
    
    app.config["SQLALCHEMY_DATABASE_URI"] = params['local_uri']

else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params['prod_uri']


db=SQLAlchemy(app)

class Contacts(db.Model):
    
    ''' class name start with capital letter,sno,name,email,phone_no,msg,date'''
    ''' below names are present in database (table- contact) field '''
    
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80),  nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_no = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)



class Posts(db.Model):
    
   
    sno = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(25),  nullable=False)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(12), nullable=True)
    date = db.Column(db.String(12), nullable=True)


@app.route('/')
def home():
    posts =Posts.query.filter_by().all() #[0:params['no_of_posts']]
    last= math.ceil(len(posts)/int(params['no_of_posts'])) 
    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts= posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts']) + int(params['no_of_posts'])]    
    if (page==1):
        prev="#"
        next="/?page="+str(page+1) 
    elif(page==last):
        prev="/?page="+str(page-1)
        next="#"
    else:
        prev="/?page=" +str(page-1)
        next= "/?page=" +str(page+1)          
    
    return render_template("index.html" ,params=params ,posts=posts ,prev=prev ,next=next)

@app.route('/about')
def about():
    return render_template("about.html" ,params=params)


@app.route('/contact',methods=['GET','POST'])
def contact():
    if(request.method == 'POST'):

        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')
        entry=Contacts(name=name,email=email,phone_no=phone,msg=message,date=datetime.now())
        db.session.add(entry)
        db.session.commit()

    return render_template("contact.html",params=params)

@app.route('/post/<string:post_slug>' ,methods=['GET'])
def post_route(post_slug):

    post=Posts.query.filter_by(slug=post_slug).first()


    return render_template("post.html", params=params ,post=post) 


@app.route('/dashboard' ,methods=['GET','POST'])
def dashboard():
    if('user' in session and  session['user'] == params['admin_nm']):
         posts = Posts.query.all()
         return render_template('dashboard.html', params=params , posts=posts)
        
    elif(request.method=='POST'):
            username=request.form.get('user_nm')
            userpass=request.form.get('password')
            if(username == params['admin_nm'] and userpass == params['admin_pass']):
                session['user']=params['admin_nm']
                posts = Posts.query.all()
                return render_template('dashboard.html', params=params , posts=posts)
            else:
            
                return render_template('login.html',params=params )
    else:
        
        return render_template('login.html',params=params)            


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/uploder", methods=['GET','POST'])
def uploder():
    if request.method == 'POST':
        if 'user' in session and session['user'] == params['admin_nm']:
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLODER_FOLDER'] ,secure_filename(f.filename)))
            return "File uploded successfully...."

@app.route("/edit/<string:sno>" , methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user']== params['admin_nm']):
        if (request.method =='POST'): 
            title = request.form.get('title')                 
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date=datetime.now()

            if sno == '0':
                post=Posts(title=title,slug=slug,content=content, date=date,img_file=img_file)

                db.session.add(post)
                db.session.commit()
                
             

            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=title                
                post.slug=slug
                post.content=content
                post.img_file=img_file
                post.date=date
                db.session.commit()
                return redirect('/edit/' +sno)
        post=Posts.query.filter_by(sno=sno).first()        
        return render_template('edit.html', params=params , post=post,sno=sno)

      

@app.route("/delete/<string:sno>", methods=['GET','POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_nm']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


app.run(debug=True)               