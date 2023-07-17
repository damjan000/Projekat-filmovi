from flask import Flask, redirect, render_template, url_for, session, request,flash
import flask
from flask_bootstrap import Bootstrap
from flask_wtf import  FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import  DataRequired
from flask_mysqldb import MySQL
import yaml
from scraper_palas import scraper


app=Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
bootstrap=Bootstrap(app)

with open('db.yaml','r') as file:
    db=yaml.safe_load(file)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql=MySQL(app)

@app.route('/')
def home():
    cur=mysql.connection.cursor()
    cur.execute("SELECT * from Movies")
    movies=cur.fetchall()
    return render_template("home.html", username=session.get('username'), movie1=movies[11], movie2=movies[121], movie3=movies[124])

@app.route('/login/', methods=['GET','POST'])
def login():
    if request.method == "POST":
        if session.get('username') is None:
            cur=mysql.connection.cursor()
            username=request.form.get('username')
            password=request.form.get('password')
            if cur.execute("SELECT * from users where username = %s and password = %s", [username, password]) > 0:
                user= cur.fetchone()
                session['login']=True
                session['username']=user[3]
                session['first_name']=user[1]
                session['last_name']=user[2]
                mysql.connection.commit()
                return redirect(url_for('home'))
            else:
                flask.flash('Neispravano korisnicko ime ili lozinka', 'danger')
                return render_template('login.html', username=session.get('username'))
        else:
            return redirect(url_for('home'))
    else:
        if session.get('username') is not None:
            return redirect(url_for('home'))
        else:
            return render_template('login.html', username=session.get('username'))
    
    return render_template('login.html', username=session.get('username'))

@app.route('/registration/', methods=['GET','POST'])
def registration():
    if request.method == 'POST':
        cur=mysql.connection.cursor()
        username=request.form.get('username')
        password=request.form.get('password')
        first_name=request.form.get('first_name')
        last_name=request.form.get('last_name')
        password_confirm=request.form.get('password_confirm')
        if password==password_confirm:
            if (cur.execute("SELECT * from users where username = %s",[username])==0) and len(username)>=5:
                cur.execute("INSERT INTO users(first_name,last_name,username,password) VALUES (%s,%s,%s,%s)",
                            [first_name,last_name,username,password])
                mysql.connection.commit()
                
                cur.close()
                flask.flash('Regiistracija uspjesna!','success')
                return redirect(url_for('login'))
            else:
                flask.flash('Username je zauzet!','danger')
                return render_template('registration.html', username=session.get('username'))
        else:
            flask.flash('Lozinka se ne poklapa!','danger')
            return render_template('registration.html', username=session.get('username'))
    return render_template('registration.html', username=session.get('username'))

@app.route('/contact/')
def contact():
    return render_template('contact.html', username=session.get('username'))

@app.route('/movies/page(<int:broj>)')
def movies(broj):
    cur=mysql.connection.cursor()
    cur.execute("SELECT * from Movies")
    num_movie=broj*8-7
    movies1=[]
    movies2=[]
    for i in cur:
        if i[0]>=num_movie and i[0]<(num_movie+4):
            movies1.append(i)
        
        elif i[0]>=(num_movie+4) and i[0]<(num_movie+8):
            movies2.append(i)
    num_page=cur.execute("SELECT * from Movies")//8
    return render_template("movies.html",username=session.get('username'),movies1=movies1, movies2=movies2, num_page=num_page)

@app.route('/movies/<int:id>', methods=['GET','POST'])
def movie(id):
    cur=mysql.connection.cursor()
    cur.execute("SELECT * from Movies where id = %s",[id])
    movie_res=cur.fetchone()
    title=movie_res[1]
    duration=movie_res[2]
    genre=movie_res[3]
    description=movie_res[4]
    img=movie_res[5]
    cur.execute("SELECT full_name from Actors where movie_id = %s",[id])
    actors=cur.fetchall()
    if request.method == 'POST':
        if session.get('username') is not None:
            comment=request.form.get('comment')
            cur.execute("SELECT id from Users where username = %s",[session.get('username')])
            user_id=cur.fetchone()
            cur.execute("INSERT INTO Reviews (movie_id, user_id, username, comment,title) VALUES (%s,%s,%s,%s,%s)"
                        ,[id, user_id, session.get('username') ,comment, title])
            mysql.connection.commit()
            
        else:
            flask.flash("Morate se prijaviti da bi ostavili komentar!","danger")
    cur.execute("SELECT * from Reviews where movie_id = %s",[id])   
    comments=cur.fetchall()
    return render_template('movie.html', username=session.get('username'), title=title, img=img,
                           genre=genre, duration=duration, description=description, comments=comments, actors=actors)

@app.route('/logout/')
def logout():
    print(session.get('login'))
    session.pop('username',None)
    return redirect(url_for('home'))

@app.route('/acount/<username>')
def acount(username):
    if session.get('username') == username:
        cur=mysql.connection.cursor()
        cur.execute("SELECT * from Reviews where username = %s",[username])
        comments=cur.fetchall()
        
        return render_template('acount.html', username=session.get('username'), comments=comments)
    else:
        return redirect(url_for('home'))
    
@app.errorhandler(404)
def e404(e):
    return render_template('404.html', username=session.get('username'))

@app.errorhandler(500)
def e500(e):
    return render_template('500.html', username=session.get('username'))
