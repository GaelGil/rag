from app import create_app
from app.extensions import db, bcrypt
from app.user.models import User

app = create_app()

with app.app_context():
    # Check if users exists
    alice_exists = User.query.filter_by(username="alice").first()
    bob_exists = User.query.filter_by(username="bob").first()
    charlie_exits = User.query.filter_by(username="charlie").first()
    new_user_exists = User.query.filter_by(username="new").first()
    another_user_exists = User.query.filter_by(username="another").first()
    user_one_exists = User.query.filter_by(username="one").first()

    # add users if they dont exist
    if (
        not alice_exists
        and not bob_exists
        and not charlie_exits
        and not another_user_exists
        and not user_one_exists
    ):
        alice = User(
            username="alice",
            email="alice@example.com",
            password=bcrypt.generate_password_hash("password").decode("utf-8"),
        )
        bob = User(
            username="bob",
            email="bob@example.com",
            password=bcrypt.generate_password_hash("password").decode("utf-8"),
        )
        charlie = User(
            username="charlie",
            email="charlie@example.com",
            password=bcrypt.generate_password_hash("password").decode("utf-8"),
        )
        new_user = User(
            username="new",
            email="alice",
            password=bcrypt.generate_password_hash("password").decode("utf-8"),
        )
        another_user = User(
            username="another",
            email="bob",
            password=bcrypt.generate_password_hash("password").decode("utf-8"),
        )
        user_one = User(
            username="one",
            email="one",
            password=bcrypt.generate_password_hash("password").decode("utf-8"),
        )

        db.session.add_all([alice, bob, charlie, new_user, another_user, user_one])
        db.session.commit()

    print("Seed data added!")
