from crypt import methods
from flask import (Flask, g, render_template, flash, redirect,
                    abort, url_for)
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)

import forms
import models 

DEBUG = True 
PORT = 8000
HOST = '0.0.0.0'


app = Flask(__name__)
app.secret_key = 'asasd;lkajsdfl;kj'

login_manager = LoginManager()
login_manager.init_app(app) # sets up login manager for application, paying attention to our view, controlling our user, getting our global object
login_manager.login_view = 'login' # if not logged in, redirect to someone for user to login

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist: # doesnotexist is something that comes from peewee
        return None

@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response

@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash('Yay, you registered!', 'success')
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash('Your email or password doesn\'t match!', 'error')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('You\'ve been logged in!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Your email or password doesn\'t match!', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user() # deletes session cookie
    flash('You\'ved been logged out! Come back soon!', 'success')
    return redirect(url_for('index'))

@app.route('/new_post', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user._get_current_object(),
                        content=form.content.data.strip())
        flash('Message posted! Thanks!', 'success')
        return redirect(url_for('index'))
    return render_template('post.html', form=form)

@app.route('/')
def index():
    stream = models.Post.select().limit(100) #check peewee docs for pagination
    return render_template('stream.html', stream=stream)

@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html' #default is w/o username, you will see your stream and posts of you and people you follow 
    if username and username != current_user.username: #if there is a user name you get that user's posts
        try:
            user = models.User.select().where(
                models.User.username**username).get() #the ** represents is 'LIKE' username, comparison that is not case sensitive
        except models.DoesNotExist:
            abort(404) #if user doesn't exist
        else:
            stream = user.posts.limit(100)
    else: #in other words it's us that is logged in
        user = current_user
        stream = current_user.get_stream().limit(100)
    if username:
        template = 'user_stream.html'
    return render_template(template, user=user, stream=stream)

@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = models.Post.select().where(models.Post.id == post_id) #interesting, I didn't create a specific id, looks like this is included
    if posts.count() == 0:
        abort(404)
    return render_template('stream.html', stream=posts)

@app.route('/follow/<username>')
@login_required
def follow(username):
    try: #find the user
        to_user = models.User.get(models.User.username**username) #try and grab username LIKE username passed in, store record in to_user... like is case insensitive
    except models.DoesNotExist: #if that user doesn't exist, do something
        pass
    else: #otherwise the user does exist
        try: #therefore we create a record in Relationships
            models.Relationship.create( #create a relationship
                from_user=g.user._get_current_object(), #current user is me
                to_user=to_user #to user is the user I want to follow
            )
        except models.IntegrityError: #this occurs b/c unique constraint; e.g. if we are creating a user that already exists
            abort(404)
        else:
            flash(f'You\'re now following {to_user.username}!', 'success')
    return redirect(url_for('stream', username=to_user.username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try: #find the user
        to_user = models.User.get(models.User.username**username) #try and grab username LIKE username passed in, store record in to_user... like is case insensitive
    except models.DoesNotExist: #if that user doesn't exist, do something
        pass
    else: #otherwise the user does exist
        try: #therefore we create a record in Relationships
            models.Relationship.get( #get a specific relationship instead of creating one like in follow
                from_user=g.user._get_current_object(), #current user is me
                to_user=to_user 
            ).delete() #delte this relationship from Relationship table
        except models.IntegrityError: #this occurs b/c unique constraint; e.g. if we are creating a user that already exists
            abort(404)
        else:
            flash(f'You\'ve unfollowed {to_user.username}!', 'success')
    return redirect(url_for('stream', username=to_user.username))

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404 #sends back status code 404 to render

if __name__ == '__main__':
    models.initialize()
    try:        
        models.User.create_user( #creating a user for myself; using create_user and not create b/c that encrypts password
            username='kennethlove',
            email='kenneth@teamtreehouse.com',
            password='password',
            admin=True
        ) 
    except ValueError:
        pass

    app.run(debug=DEBUG, host=HOST, port=PORT)
    