import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from utils.steam_api import get_steam_game_details, get_featured_games
from dotenv import load_dotenv
from flask_migrate import Migrate


load_dotenv()

# ---- App Setup ---- #
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey123")
app.config['STEAM_API_KEY'] = os.getenv('STEAM_API_KEY')

# ---- Database ---- #
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ---- Models ---- #
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    subtitle = db.Column(db.String(250))
    author = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

# ---- Forms ---- #
class ReviewForm(FlaskForm):
    user_name = StringField('Your Name', validators=[DataRequired()])
    rating = IntegerField('Rating (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit Review')

# ---- Routes ---- #

@app.route('/')
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    try:
        games = get_featured_games()


        for g in games:
            g['game_image_url'] = g.get("image_url") or url_for('static', filename='img/placeholder.png')
    except Exception as e:
        print("Steam API error:", e)
        games = []

    return render_template('index.html', posts=posts, games=games)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        new_msg = ContactMessage(name=name, email=email, subject=subject, message=message)
        db.session.add(new_msg)
        db.session.commit()
        flash("Message saved!", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/sample-post')
def sample_post():
    post = Post.query.first()
    if not post:
        post = Post(
            title="Sample Post",
            subtitle="Welcome to CodeCritical!",
            author="Admin",
            content="This is your first sample post. Add more posts using the 'New Post' page!"
        )
        db.session.add(post)
        db.session.commit()
    return render_template('post.html', post=post)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        author = request.form['author']
        content = request.form['content']
        post = Post(title=title, subtitle=subtitle, author=author, content=content)
        db.session.add(post)
        db.session.commit()
        flash("New post created!", "success")
        return redirect(url_for('home'))
    return render_template('new_post.html')

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.subtitle = request.form['subtitle']
        post.content = request.form['content']
        db.session.commit()
        flash("Post updated!", "success")
        return redirect(url_for('post', post_id=post.id))
    return render_template('edit_post.html', post=post)

@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted!", "success")
    return redirect(url_for('home'))

@app.route('/game/<int:appid>', methods=['GET', 'POST'])
def game_page(appid):
    try:
        game = get_steam_game_details(appid)
        if not game:
            flash("Game not found.", "warning")
            return redirect(url_for('home'))
        # Ensure image_url exists
        game_image_url = game.get("image_url") or url_for('static', filename='img/placeholder.png')
    except Exception as e:
        print("Steam API error:", e)
        flash("Error fetching game data.", "danger")
        return redirect(url_for('home'))

    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            game_id=appid,
            user_name=form.user_name.data,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('game_page', appid=appid))

    reviews = Review.query.filter_by(game_id=appid).order_by(Review.date_posted.desc()).all()
    return render_template(
        'game_details.html',
        game=game,
        form=form,
        reviews=reviews,
        game_image_url=game_image_url
    )

# ---- Run Server ---- #
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
