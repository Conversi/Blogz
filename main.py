from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:LaunchCode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_post = db.Column(db.Text())

    def __init__(self, blog_title, blog_post):
        self.blog_title = blog_title
        self.blog_post = blog_post

@app.route('/blog', methods=['POST', 'GET'])
def home():
    list_blog = Blog.query.all()
    return render_template('blog.html', list_blog=list_blog)

@app.route('/newpost', methods=['POST', 'GET'])
def validate_blog():
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
def solo():
    blog_id = request.args.get('id')
    query_title = Blog.query.get(blog_id).blog_title
    query_post = Blog.query.get(blog_id).blog_post
    # print ('xxxxxxxxxxxxxx', query, 'xxxxxxxxxxxxxxxx')
    return render_template ('single_blog.html', query_title=query_title, query_post=query_post)

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect ('/blog')

if __name__ == '__main__':
    app.run()