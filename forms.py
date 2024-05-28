from flask_wtf import FlaskForm
from wtforms import FloatField, TextAreaField, IntegerField, StringField, SubmitField
from wtforms.validators import InputRequired, NumberRange, URL, DataRequired


class AddMovieForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    year = IntegerField('Year', validators=[InputRequired(), NumberRange(min=1800, max=2100)])
    description = TextAreaField('Description', validators=[InputRequired()])
    rating = FloatField('Rating', validators=[InputRequired(), NumberRange(min=0, max=10)])
    ranking = IntegerField('Ranking', validators=[InputRequired(), NumberRange(max=10)])
    review = TextAreaField('Review')
    img_url = StringField('Image', validators=[InputRequired(), URL()])
    submit = SubmitField("Done")


class EditMovieForm(FlaskForm):
    rating = FloatField('Rating', validators=[DataRequired(), NumberRange(min=0, max=10)])
    review = TextAreaField('Review', validators=[DataRequired()])
    submit = SubmitField("Update")


class FindMovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField("Add a movie")


