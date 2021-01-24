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

@app.route('/signin', methods=['POST','GET'])
def signin():
	if request.method == "POST":
		session.permanent = True
		name = request.form["name"]
		email = request.form["email"]
		password = request.form["password"]
		found_user = User.query.filter_by(name=name).first()
		if not found_user:
			user = User(name,email,password)
			db.session.add(user)
			db.session.commit()
			session["name"] = name
			session["email"] = email
			session["password"] = password
			flash('Email already in use.')
			return redirect(url_for("home"))
		else:
			#user already exists
			pass
			return redirect(url_for("home"))
	else :
		if "name" in session:
			return redirect(url_for("home"))
		return render_template("signin.html", title="Sign In")

@app.route("/logout")
def logout():
	session.pop("name", None)
	session.pop("email", None)
	return redirect(url_for("signin"))

if __name__ == '__main__':
	db.create_all()
	postHandler = PostHandler()
	post1 = postHandler.add_post('this is title', 'vedant singh', 'Lorem ipsum said that autocomplete in sublime text is not working i dont know why and it enough')
	app.run(debug=True)