from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "nextflick123"

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/movie/<movie_name>")
def movie_details(movie_name):

    connection = sqlite3.connect("nextflick.db")
    cursor = connection.cursor()
    
    cursor.execute(
    """
    SELECT
        movie_name,
        ROUND(AVG(rating), 2),
        COUNT(*),
        category, poster
    FROM movies
    WHERE LOWER(TRIM(movie_name)) = LOWER(TRIM(?))
    GROUP BY movie_name
    """,
    (movie_name,)
)

    
    movie = cursor.fetchone()
    
    cursor.execute(
    """
    SELECT rating
    FROM movies
    WHERE LOWER(movie_name) = LOWER(?)
    ORDER BY rating DESC
    """,
    (movie_name,)
)

    ratings = cursor.fetchall()

    connection.close()
   

    return render_template(
        "movie_details.html",
        movie=movie,
        ratings=ratings
    )

@app.route("/rate", methods=["GET", "POST"])
def rate():

    connection = sqlite3.connect("nextflick.db")
    cursor = connection.cursor()
 
    connection.commit()

    # Add Movie
    if request.method == "POST":

        movie = request.form.get("movie").strip().title()
        rating = request.form.get("rating")
        genre = request.form.get("genre").strip()
        poster = request.form.get("poster")
       

        cursor.execute(
            """
            INSERT INTO movies (movie_name, rating, category, poster)
            VALUES (?, ?, ?, ?)
            """,
            (movie, rating, genre, poster)
        )

        connection.commit()
        flash("Movie Added Successfully ✅")

    # Search
    genre_filter = request.args.get("genre_filter")
    search = request.args.get("search")
    if search:
        cursor.execute(
        """
        SELECT * FROM movies
        WHERE LOWER(movie_name) LIKE LOWER(?) 
        """,
        ('%' + search + '%',)
        )

        movies = cursor.fetchall()
    
    else:
        cursor.execute(
        """
        SELECT * FROM movies
        """
        )

        movies = cursor.fetchall()


    cursor.execute(
    """
    SELECT * FROM movies
    """
    )
    all_movies = cursor.fetchall()

    
    if search:

        cursor.execute(
            """
            SELECT min(id),
                movie_name,
                ROUND(AVG(rating), 2),
                COUNT(*),
                category, poster
            FROM movies
            WHERE movie_name LIKE ?
            GROUP BY movie_name
            ORDER BY AVG(rating) DESC
            """,
            ('%' + search + '%',)
        )
    elif genre_filter:
        cursor.execute(
        """
        SELECT
            min(id),
            movie_name,
            ROUND(AVG(rating),2),
            COUNT(*),
            category,
            poster
        FROM movies
        WHERE category = ?
        GROUP BY movie_name
        ORDER BY AVG(rating) DESC
        """,
        (genre_filter,)
    )

    else:

        cursor.execute(
            """
            SELECT min(id),
                movie_name,
                ROUND(AVG(rating), 2),
                COUNT(*),
                category, poster
            FROM movies
            GROUP BY movie_name
            ORDER BY AVG(rating) DESC
            """
        )

    movie_summary = cursor.fetchall()
   

    cursor.execute(
          """ select
        movie_name,
        ROUND(AVG(rating), 2),
        COUNT(*),
        category
    FROM movies
    GROUP BY movie_name
    ORDER BY AVG(rating) DESC
    LIMIT 5 """
)

    recommended_movies = cursor.fetchall()

    
    top_movie = None

    if len(movies) > 0:
        top_movie = max(all_movies, key=lambda movie: movie[2])


    ratings_list = []
    for movie in all_movies:
        ratings_list.append(movie[2])
        cursor.execute("""
SELECT category, COUNT(*)
FROM movies
GROUP BY category
ORDER BY COUNT(*) DESC
""")

    genre_stats = cursor.fetchall()

    total_movies = len(ratings_list)

    if total_movies > 0:
        average_rating = round(sum(ratings_list) / total_movies, 2)
        highest_rating = max(ratings_list)
    else:
        average_rating = 0
        highest_rating = 0

   
    
    connection.close()
    return render_template(
        "rate.html",
        movies=movies,
        movie_summary=movie_summary,
        total_movies=total_movies,
        average_rating=average_rating,
        highest_rating=highest_rating,
        top_movie=top_movie,
        recommended_movies=recommended_movies,
        genre_stats=genre_stats
    )

@app.route("/delete/<int:id>")
def delete(id):

    connection = sqlite3.connect("nextflick.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM movies
        WHERE id = ?
        """,
        (id,)
    )

    connection.commit()
    flash("Movie Deleted Successfully 🗑️✅")
    connection.close()

    return redirect("/rate")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    connection = sqlite3.connect("nextflick.db")
    cursor = connection.cursor()

    if request.method == "POST":

        new_rating = request.form.get("rating")

        cursor.execute(
            """
            UPDATE movies
            SET rating = ?
            WHERE id = ?
            """,
            (new_rating, id)
        )

        connection.commit()
        flash("Rating Updated Successfully ✏️✅")
        connection.close()

        return redirect("/rate")

    cursor.execute(
        """
        SELECT * FROM movies
        WHERE id = ?
        """,
        (id,)
    )

    movie = cursor.fetchone()

    connection.close()

    return render_template(
        "edit.html",
        movie=movie
    )


app.run(debug=True)