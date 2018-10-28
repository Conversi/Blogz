from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:LaunchCode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_post = db.Column(db.Text())
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_post):
        self.blog_title = blog_title
        self.blog_post = blog_post

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('register.html')

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    
    owner = User.query.filter_by(username=session['username']).first()
    
    list_blog = Blog.query.all()
    return render_template('blog.html', list_blog=list_blog)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    list_blog = Blog.query.all()
    if request.method == 'POST':
        blog_post = request.form['blog_post']
        blog_title = request.form['blog_title']
        post_error = ''
        title_error =''
        
        if not blog_post:
            post_error = 'May not leave blank'

        if not blog_title:
            title_error = 'May not leave blank'

        if not blog_post or not blog_title:
            return render_template('newpost.html', title='Build-A-Blog', blog_post=blog_post,
            blog_title=blog_title, post_error=post_error, title_error=title_error, list_blog=list_blog)
    
        new_blog = Blog(blog_title, blog_post)
        db.session.add(new_blog)        
        db.session.commit()
        return redirect ('/blog')

    return render_template ('newpost.html', list_blog=list_blog)

@app.route('/single_blog', methods=['GET'])
def single_blog():
    blog_id = request.args.get('id')
    query_title = Blog.query.get(blog_id).blog_title
    query_post = Blog.query.get(blog_id).blog_post
    # print ('xxxxxxxxxxxxxx', query, 'xxxxxxxxxxxxxxxx')
    return render_template ('single_blog.html', query_title=query_title, query_post=query_post)

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect ('/blog')

if __name__ == '__main__':
    app.run()