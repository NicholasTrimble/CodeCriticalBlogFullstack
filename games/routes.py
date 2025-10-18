from flask import render_template, redirect, url_for, flash
from . import games_bp
from models import Review, db
from forms import ReviewForm
from utils.rawg_api import fetch_game_details

@games_bp.route('/game/<int:game_id>', methods=['GET', 'POST'])
def game_page(game_id):
    # Get game info from RAWG API
    game = fetch_game_details(game_id)

    # Review submission
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            game_id=game_id,
            user_name=form.user_name.data,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('games.game_page', game_id=game_id))

    # Fetch all reviews for this game
    reviews = Review.query.filter_by(game_id=game_id).all()
    return render_template('game_details.html', game=game, form=form, reviews=reviews)