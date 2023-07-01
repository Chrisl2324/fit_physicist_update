from flask import Flask, flash, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, EmailField
from wtforms.validators import DataRequired, Email, InputRequired, email_validator
from flask_migrate import Migrate
from sqlalchemy import text



app = Flask(__name__, static_url_path='/static')
app.config['MAIL_SERVER'] = 'smtp@gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'clombar1@email.essex.edu'
app.config['MAIL_PASSWORD'] = '232425'

mail = Mail(app)


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
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.Column(db.String, nullable=False)

    user = db.relationship("User", backref=db.backref("articles", lazy=True))
    comments = db.relationship("Comment", back_populates="article")

    def __repr__(self):
        return f"Article <{self.title}>"


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False)

    user = db.relationship("User", backref=db.backref("comments", lazy=True))
    article = db.relationship("Article", back_populates="comments")

    def __repr__(self):
        return f"Comment <{self.text}>"

    
class CommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    content = StringField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')



        
with app.app_context():
    db.create_all()
        
    
@app.route('/about')
def about():
    return render_template('about.html', title="The Fit Physicist-About")
    
@app.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        sender = request.form.get('name')
        email = request.form.get('email')
        title = request.form.get('title')
        message = request.form.get('message')
        priority = request.form.get('priority')
            
        msg = Message(title, sender=email, recipients=['clombar1@email.essex.edu'])
        msg.body = f"Name: {sender}\nEmail: {email}\n\n{message}"
        mail.send(msg)

        return 'Email sent!'
    
    return render_template('contact.html')

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/submit_comment/<int:article_id>', methods=["POST"])
@login_required
def submit_comment(article_id):
    article = Article.query.get_or_404(article_id)
    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        comment = Comment(
            text=comment_form.content.data,
            user=current_user,
            article=article
        )
        db.session.add(comment)
        db.session.commit()
        flash("Comment submitted successfully!")
        return redirect(url_for('article', article_id=article_id))

    return render_template('comment_form.html', comment_form=comment_form)

@app.route('/', methods=["GET", "POST"])
def index():
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
                flash(f"Hello {username}, Welcome to the Fit Physicist!")
                return jsonify(message="Login successful")

            flash("Incorrect login information! Try again")
            return jsonify(message="Login failed")
                
    # Handle GET request or other cases
    articles = Article.query.all()
    context = {
        "articles": articles
    }

    return render_template('index.html', title='The Fit Physicist', **context)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for('index'))

@app.route('/all_articles')
@login_required
def all_articles():
    articles = Article.query.all()
    comment_form = CommentForm()

    return render_template('all_articles.html', title="All Articles", articles=articles, comment_form=comment_form)

@app.route('/article')
def article():
    
    article_previews = [
        { 
            'title': 'Calisthenics Primer',
            'description': "A beginner's intro to calisthenics, with workout plans and other advice",
            'image': 'https://www.dmarge.com/wp-content/uploads/2022/01/most-difficult-handstand-1200x800.jpg',
            'url': '#',
        },
        {
            'title': 'Basic Nutrition Advice',
            'description': "This is a good starting point for those just starting to track their diets",
            'image': 'http://worldonline.media.clients.ellingtoncms.com/img/croppedphotos/2017/02/27/healthy-diet_t640.jpg?a6ea3ebd4438a44b86d2e9c39ecf7613005fe067',
            'url': '#',
        },
        {
            'title': 'Cardio Workouts',
            'description': 'Various workouts based on circuit-style, designed for maximum calorie burn',
            'image': 'https://www.shape.com/thmb/qr6AnPByfid8VTqqv9nrKgJOUr0=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/best-cardio-exercises-promo-2000-498cbfb8f07541b78572bf810e7fb600.jpg',
            'url': url_for('cardio_article')
        },
        {
            'title': 'Deadlift Basics',
            'description': 'This article provides the basic setup and techniques of the deaflift movement',
            'image': 'https://www.americanfootballinternational.com/wp-content/uploads/Barbend-2021-Deadlift-620x400.png',
            'url': '#'
        },
        {
            'title': 'Supplementation',
            'description': 'My personal experience with supplements and discussion of my favorite brands',
            'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSbwctv2YulNCDZ5JTwRK9ry8yz-D1cY-GU1Q&usqp=CAU',
            'url': '#',
        },
        {
            'title': 'Recovery',
            'description': 'Various techniques to enhance and facilitate recovery from strenous exercise',
            'image': 'https://images.pexels.com/photos/3076509/pexels-photo-3076509.jpeg?auto=compress&cs=tinysrgb&w=600',
            'url': url_for('cardio_article')
        }
    ]

    return render_template('article.html', title="Articles", articles=article_previews)

@app.route('/contribute', methods=["GET", "POST"])
@login_required
def contribute():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        user_id = current_user.id
        author = current_user.username

        title_exists = Article.query.filter_by(title=title).first()
        if title_exists:
            flash("This article already exists. Please choose a new title.")
            return redirect(url_for('contribute'))
        
        new_article = Article(title=title, content=content, user_id=user_id, author=author)
        db.session.add(new_article)
        db.session.commit()

        flash("Thanks for sharing with us!")
        return redirect(url_for('index'))
    
    return render_template('contribute.html', title="The Fit Physicist-Contribute")

@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html', title="Welcome to the Fit Physicist")

@app.route('/cardio_workouts')
def cardio_article():
    return render_template('cardio_workouts.html', title="Cardio Workouts")

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('error.html', error_code=401, error_message="Please Log in to View this Page"), 401

@app.route('/search')
def search():
    query = request.args.get('query')
    articles = Article.query.filter(Article.title.ilike(f'%{query}%')).all()

    context = {
        "articles": articles
    }
    return render_template('search_results.html', title="Search Results", query=query, **context)

@app.route('/single_article/<int:article_id>')
def single_article(article_id):
    article = Article.query.get_or_404(article_id)
    comments = Comment.query.filter_by(article_id=article_id).all()
    return render_template('single_article.html', title="The Fit Physicist", article=article, comments=comments)

    
@app.route('/edit/<int:id>', methods=["GET", "POST"])
@login_required
def edit(id):
    article_edit = Article.query.get_or_404(id)

    if current_user.username == article_edit.author:
        if request.method == 'POST':
            new_title = request.form.get('title')
            new_content = request.form.get('content')

            if new_title and new_content:  # Ensure the new title is not empty
                article_edit.title = new_title
                article_edit.content = new_content

            db.session.commit()

            flash("Your changes have been saved")
            return redirect(url_for('all_articles'))

        return render_template('edit.html', article=article_edit)
    
    flash("You cannot edit another user's article!")
    return render_template('index.html', title='The Fit Physicist')

@app.route('/delete/<int:id>/', methods=['GET'])
@login_required
def delete(id):
    article_to_delete = Article.query.get_or_404(id)

    if current_user.username == article_to_delete.author:
        db.session.delete(article_to_delete)
        db.session.commit()
        flash("Your article has been deleted")
        return redirect(url_for('index'))
    
    flash('You are not authorized to delete this article!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False)
            