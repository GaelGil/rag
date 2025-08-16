from app import create_app
from app.extensions import db, bcrypt
from app.user.models import User
from app.chat.models import Movie
import os
import pickle

app = create_app()

with app.app_context():
    # Check if admind exists

    admin_exists = User.query.filter_by(username="admin").first()

    # add admind if not exists
    if not admin_exists:
        admin = User(
            username="admin",
            email="admin@admin.com",
            password=bcrypt.generate_password_hash("password").decode("utf-8"),
        )

        db.session.add_all([admin])
        db.session.commit()

    with os.scandir("./app/chat/agent/utils/embeddings/") as entries:
        for entry in entries:  # Iterate over the entries
            if entry.is_file():  # Check if the entry is a file
                print(entry.path)  # Print the file path
                # Check if the movie already exists
                exists = Movie.query.filter_by(title=entry.name).first()
                if not exists:  # if it doesnt exists
                    # get the movie embedding
                    with open(
                        "./app/chat/agent/utils/embeddings/" + entry.name, "rb"
                    ) as f:
                        # load the embedding
                        movie_emembedding = pickle.load(f)
                        # create movie object and add embedding
                        movie = Movie(
                            title=entry.name,
                            embedding=movie_emembedding.data[0].embedding,
                        )
                        # add movie
                        db.session.add(movie)
                        # commit
                        db.session.commit()

    print("Seed data added!")
