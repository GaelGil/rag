from app.user.controllers import users


def register_routes(app):
    app.register_blueprint(users)
