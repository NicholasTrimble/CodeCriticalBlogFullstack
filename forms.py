from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ReviewForm(FlaskForm):
    user_name = StringField('Your Name', validators=[DataRequired()])
    rating = IntegerField('Rating (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit Review')