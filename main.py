from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import requests
from instance import config
from flask_migrate import Migrate
from forms import *

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
bootstrap = Bootstrap4(app)


app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Movie(db.Model):
    __tablename__ = "movie"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False, default=0)
    ranking = db.Column(db.Integer, nullable=False, default=0)
    review = db.Column(db.Text, nullable=False, default="")
    img_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'Movie {self.title} - {self.year}'


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies = result.scalars().all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
        db.session.commit()

    print(all_movies)
    return render_template("index.html", movies=all_movies, boostrap=bootstrap)


@app.route("/edit_movie/<int:movie_id>", methods=['GET', 'POST'])
def edit_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = EditMovieForm(obj=movie)
    if request.method == 'POST' and form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data

        db.session.commit()
        print("Successfully updated the movie!")
        return redirect(url_for('home'))
    else:
        print("Failed to validate form or another issue occurred.")
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error in {field}: {error}")
    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete_movie/<int:movie_id>", methods=["POST"])
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie:
        try:
            db.session.delete(movie)
            db.session.commit()
            print("Movie deleted successfully!")
        except SQLAlchemyError as e:
            print("Error deleting movie: ", str(e))
            db.session.rollback()

    return redirect(url_for('home'))


@app.route("/add_movie", methods=["GET", "POST"])
def add_movie():
    form = FindMovieForm()
    if form.validate_on_submit():
        movie = Movie(
            title=form.title.data
        )
        url = "https://api.themoviedb.org/3/search/movie"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {config.TMDB_API_KEY}"
        }
        params = {
            "query": movie.title,
            "include_adult": "false",
            "language": "en-US",
            "page": 1
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            movie_data = response.json()
            if "results" in movie_data and len(movie_data["results"]) > 0:
                flash("Film found successfully.", "success")
                return render_template("select.html", movies=movie_data["results"])
            else:
                flash("No films found.", "info")
                return render_template("add.html", form=form)
        else:
            flash("Error while trying to get movies.", "error")
            return render_template("add.html", form=form)
    return render_template("add.html", form=form)


@app.route('/find')
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_url = f"{config.SELECTED_MOVIE}/{movie_api_id}"
        response = requests.get(movie_url, params={"api_key": config.TMDB_AUTH_TOKEN, "language": "en-US"})
        if response.status_code == 200:
            data = response.json()
            new_movie = Movie(
                title=data["title"],
                year=data["release_date"].split("-")[0],
                description=data["overview"],
                img_url=f"{config.TMDB_IMAGE_URL}{data['poster_path']}"
            )
            db.session.add(new_movie)
            db.session.commit()
            return redirect(url_for("edit_movie", movie_id=new_movie.id))
        else:
            print(response.status_code)
            flash("Failed to find movie in the database.", "error")
            return render_template("add.html", form=FindMovieForm())
    flash("No movie ID provided.", "error")
    return redirect(url_for("add_movie"))


if __name__ == '__main__':
    app.run(debug=True)
