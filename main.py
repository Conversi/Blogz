from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashutils import make_password, check_password

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:LaunchCode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'asdfasdf'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.Text)
    blog_post = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blog_date = db.Column(db.DateTime)

    def __init__(self, blog_title, blog_post, owner, blog_date=None):
        self.blog_title = blog_title
        self.blog_post = blog_post
        self.owner = owner
        if blog_date is None:
            blog_date = datetime.utcnow()
        self.blog_date = blog_date

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = make_password(password)

@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'index', 'signup', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    post_id = request.args.get('id')
    author_id = request.args.get('owner_id')
    list_blog = Blog.query.all()
    if post_id:
        single_post = Blog.query.get(post_id)
        return render_template('singlePost.html', posts=single_post)
    if author_id:
        posts_from_author = Blog.query.filter_by(owner_id=author_id)
        return render_template('singleUser.html', posts=posts_from_author)
    
    return render_template('blog.html', posts=list_blog)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['Password']

        user = User.query.filter_by(username=username).first()

        username_error = ''
        password_error = ''

        if not username and not password:
            username_error = "Username invalid"
            password_error = "Password invalid"
            return render_template('login.html', username_error=username_error, password_error=password_error)
        if not password:
            password_error = "Password invalid"
            return render_template('login.html', password_error=password_error, username=username)
        if not username:
            username_error = "Username invalid"
            return render_template('login.html', username_error=username_error)

        if user and check_password(password, user.password):
            session['username'] = username
            return redirect('/newpost')
        if user and not user.password == password:
            password_error = "Password invalid"
            return render_template('login.html', password_error=password_error, username=username)
        if not user:
            username_error = "Username invalid"
            return render_template('login.html', username_error=username_error)
    else:
        return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['Password']
        verify = request.form['VerifyPassword']

        username_error = ''
        password_error = ''
        verify_error = ''

        existing_user = User.query.filter_by(username=username).first()
        
        if not username or not password or not verify:
            username_error = "Username required."
            return render_template('signup.html', username_error=username_error)
        
        if len(username) < 3:
            username_error = "Invalid username. Must be at least three characters."
            return render_template('signup.html', username_error=username_error)
        if len(password) < 3:
            password_error = "Invalid password. Must be at least three characters."
            return render_template('signup.html', password_error=password_error, username=username)

        if existing_user:
            username_error = "Username already exists."
            return render_template('signup.html', username_error=username_error)

        if not existing_user and not password==verify:
            password_error = "Passwords do not match"
            verify_error = "Passwords do not match"
            return render_template('signup.html', username=username, password_error=password_error, verify_error=verify_error)

        if not existing_user and password==verify:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        
    else: 
        return render_template('signup.html')

@app.route('/newpost', methods=['GET', 'POST'])
def add_entry():

    if request.method == 'POST':
        title_error = ''
        blog_post_error = ''

        blog_title = request.form['blog_title']
        blog_post = request.form['blog_post']
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(blog_title, blog_post, owner)

        if blog_title and blog_post:
            db.session.add(new_post)
            db.session.commit()
            post_link = "/blog?id=" + str(new_post.id)
            return redirect(post_link)
        else:
            if not blog_title and  not blog_post:
                title_error = "A title is required"
                blog_post_error = "A post is required"
                return render_template('newpost.html', title_error=title_error, blog_post_error=blog_post_error, blog_title=blog_title, blog_post=blog_post)
            elif not blog_title:
                title_error = "A title is required"
                return render_template('newpost.html', title_error=title_error, blog_post=blog_post, blog_title=blog_title)
            elif not blog_post:
                blog_post_error = "A post is required"
                return render_template('newpost.html', blog_post_error=blog_post_error, blog_post=blog_post, blog_title=blog_title)

    else: 
        return render_template('newpost.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')
    
@app.route('/')
def index():
    all_users = User.query.distinct()
    return render_template('index.html', usernames=all_users)

if __name__ == '__main__':
    app.run()