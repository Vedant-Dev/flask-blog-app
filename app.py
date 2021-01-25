from flask import Flask, render_template, url_for, redirect, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "thisisakey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.sqlite3'
app.config['SQLALCHEMY_BINDS'] = {
	'user' : 'sqlite:///users.sqlite3'
}
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.permanent_session_lifetime = timedelta(days=7)
db = SQLAlchemy(app)

class PostHandler():
	def add_post(self, title, author, body):
		search_result = Post.query.filter_by(title=title).first()
		if not search_result:
			post = Post(title=title,author=author,body=body)
			db.session.add(post)
			db.session.commit()
			return 1
		else:
			return 0
	def delete(self,title):
		search_result = Post.query.filter_by(title=title).first()
		if search_result:
			db.session.delete(search_result)
			db.session.commit()
			return 1
		else:
			return 0
	def clear_database(self):
		posts = Post.query.all()
		for post in posts:
			db.session.delete(post)
		db.session.commit()

	def all_post(self):
		return Post.query.all()

class Post(db.Model):
	id = db.Column('id',db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	author = db.Column(db.String(100), nullable=False)
	body = db.Column(db.String(500), nullable=False)

	def __init__(self, title, author, body):
		self.title = title
		self.author = author
		self.body = body

class User(db.Model):
	__bind_key__ = 'user'
	id = db.Column('id',db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)
	email = db.Column(db.String, nullable=False)
	password = db.Column(db.String, nullable=False)

	def __init__(self, name, email, password):
		self.name = name
		self.email = email
		self.password = password

@app.route('/')
def home():
	return render_template('home.html', title='Home Page', posts=postHandler.all_post())
@app.route('/view')
def view():
	return render_template('view.html', values=User.query.all())

@app.route('/signup', methods=['POST','GET'])
def signup():
	if request.method == "POST":
		session.permanent = True
		name = request.form["name"]
		email = request.form["email"]
		password = request.form["password"]
		found_user = User.query.filter_by(email=email).first()
		if not found_user:
			user = User(name,email,password)
			db.session.add(user)
			db.session.commit()
			session["name"] = name
			session["email"] = email
			session["password"] = password
			flash('Signed up.')
			return redirect(url_for("home"))
		else:
			flash('Email already in use.')
			return redirect(url_for("home"))
	else :
		if "name" in session:
			flash('Already logged in...')
			return redirect(url_for("home"))
		return render_template("signup.html", title="Sign Up")

@app.route('/signin', methods=['POST','GET'])
def signin():
	if request.method == "POST":
		session.permanent = True
		email = request.form["email"]
		password = request.form["password"]
		found_user = User.query.filter_by(email=email).first()
		if found_user:
			if password == found_user.password:
				session["name"] = found_user.name
				session["email"] = email
				session["password"] = password
				flash('Signed in.')
				return redirect(url_for("home"))
			else:
				flash('Wrong password')
				return render_template("signin.html", title="Sign Up")
			
		else:
			flash('User doesn\'t exists')
			return render_template("signin.html", title="Sign Up")
	else :
		if "name" in session:
			return redirect(url_for("home"))
		return render_template("signin.html", title="Sign In")

@app.route('/read/<title>')
def read(title):
	post = Post.query.filter_by(title=title).first()
	if post:
		return render_template('read.html', title=title, post=post)
	else:
		return render_template('read.html', title='Error 404!', post='Not found')
	
@app.route("/logout")
def logout():
	session.pop("name", None)
	session.pop("email", None)
	session.pop("password", None)
	return redirect(url_for("signin"))

if __name__ == '__main__':
	db.create_all()
	postHandler = PostHandler()
	post1 = postHandler.add_post('this is title', 'vedant singh', 'Lorem ipsum said that autocomplete in sublime text is not working i dont know why and it enough')
	app.run(debug=True)