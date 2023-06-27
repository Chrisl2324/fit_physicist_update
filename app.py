from flask import Flask, flash, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import UserMixin, LoginManager, login_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify



app = Flask(__name__, static_url_path='/static')



base_dir = os.path.dirname(os.path.realpath(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + \
    os.path.join(base_dir, 'chris_blog.db')
app.config["SQLACLHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = 'you-will-never-guess1315123'

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(50), nullable=False, unique=True)
    last_name = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    
def __repr__(self):
    return f"User <{self.username}>"

class Article(db.Model):
    __tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey(
        "users.id"), unique=False, nullable=False)
    author = db.Column(db.String, nullable=False)
    
    def __repr__(self):
        return f"Article <{self.title}>"
    
class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String, nullable=False)
    priority = db.Column(db.String(20))
        
    def __repr__(self):
            return f"Message: <{self.title}>"
        
with app.app_context():
    db.create_all()
        
    
@app.route('/about')
def about():
    return render_template('about.html', title="About")
    
@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        sender = request.form.get('name')
        email = request.form.get('email')
        title = request.form.get('title')
        message = request.form.get('message')
        priority = request.form.get('priority')
            
        new_message = Message(sender=sender, email=email,
        title=title, message=message, priority=priority)
        
        db.session.add(new_message)
        db.session.commit()
        
        flash("Message sent. Thanks for reaching out!")
        return redirect(url_for('index'))
    
    return render_template('contact.html')

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        action = request.json.get('action')
        if action == 'register':
            # Registration logic
            username = request.json.get('username')
            first_name = request.json.get('first_name')
            last_name = request.json.get('last_name')
            email = request.json.get('email')
            password = request.json.get('password')

            # Validate form values
            if not username or not first_name or not last_name or not email or not password:
                return jsonify(message="Please fill in all fields"), 400

            # Check if username or email already exists
            username_exists = User.query.filter_by(username=username).first()
            if username_exists:
                return jsonify(message="This username already exists"), 400

            email_exists = User.query.filter_by(email=email).first()
            if email_exists:
                return jsonify(message="This email is already registered"), 400

            # Create a new user
            password_hash = generate_password_hash(password)
            new_user = User(username=username, first_name=first_name, last_name=last_name, email=email, password_hash=password_hash)
            db.session.add(new_user)
            db.session.commit()

            return jsonify(message="Sign up successful")

        elif action == 'login':
            # Login logic
            username = request.json.get('username')
            password = request.json.get('password')

            print(f"Received username: {username}")
            print(f"Received password: {password}")

            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                flash('You are now logged in!')
                return jsonify(message="Login successful")

            flash("Incorrect login information! Try again")
            return jsonify(message="Login failed")

    # Handle GET request or other cases
    articles = Article.query.all()
    context = {
        "articles": articles
    }

    return render_template('practice.html', title='Home', **context)


if __name__ == '__main__':
    app.run(debug=True)
            