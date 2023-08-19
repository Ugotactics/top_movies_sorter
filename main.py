from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.app_context().push()
Bootstrap(app)
db_path = os.path.join(os.path.dirname(__file__),
                       '/top-movies.db')
db_uri = 'sqlite:///{}'.format(db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)






class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=True)
    year = db.Column(db.String(250), unique=False, nullable=True)
    description = db.Column(db.String(250), unique=False, nullable=True)
    rating = db.Column(db.String(250), unique=False, nullable=True)
    ranking = db.Column(db.String(250), unique=False, nullable=True)
    review = db.Column(db.String(250), unique=False, nullable=True)
    img_url = db.Column(db.String(250), unique=False, nullable=True)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Movie {self.title}>'


class RateMovieForm(FlaskForm):
    rating = StringField('Your rating out of 10 e.g. 8.5')
    review = StringField('Your review')
    submit = SubmitField('done')


class AddMovie(FlaskForm):
    added_movie = StringField('Movie Title')
    add_button = SubmitField('Done')


db.create_all()


def sort_list(movie):
    return movie.rating


@app.route("/")
def home():
    all_movies = Movie.query.all()
    all_movies.sort(key=sort_list, reverse=True)
    for i in range(len(all_movies)):
        all_movies[i].ranking = i + 1
    db.session.commit()
    return render_template("index.html", all_movies=all_movies)


@app.route("/edit", methods=['POST', 'GET'])
def edit_rating():
    movie_id = request.args.get('movie_id')
    movie_form = RateMovieForm()
    movie_to_update = Movie.query.get(movie_id)
    if movie_form.validate_on_submit():
        print(movie_form.data)
        movie_to_update.rating = float(movie_form.rating.data)
        movie_to_update.review = movie_form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", form=movie_form, movie_id=movie_id)


@app.route("/delete")
def delete_movie():
    movie_id = request.args.get('movie_id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['POST', 'GET'])
def add_movie():
    form = AddMovie()
    if request.method == 'POST':
        movie_name = form.added_movie.data
        url = 'https://api.themoviedb.org/3/search/movie'
        params = {
            "api_key": "e2aedc76015eecc2fc972b5c0275ff5c",
            "query": movie_name
        }
        all_movies = []
        response = requests.get(url, params=params)
        json_response = response.json()
        results = json_response["results"]
        for result in results:
            print(results)
            release_date = result["release_date"]
            movie_title = result["original_title"]
            movie_id = result["id"]
            movie_data = (movie_title, release_date, movie_id)
            all_movies.append(movie_data)
        return render_template('select.html', all_movies=all_movies)
    return render_template('add.html', form=form)


@app.route("/movie", methods=["POST", "GET"])
def selected_movie():
    request_id = request.args.get("id")
    if request_id:
        url = f'https://api.themoviedb.org/3/movie/{request_id}'
        params = {
            "api_key": "e2aedc76015eecc2fc972b5c0275ff5c",
        }
        id_response = requests.get(url, params=params)
        data = id_response.json()
        movie_image_url = "https://image.tmdb.org/t/p/w500"
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{movie_image_url}{data['poster_path']}",
            description=data["overview"],
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit_rating", movie_id=new_movie.id))






if __name__ == '__main__':
    app.run(debug=True)
