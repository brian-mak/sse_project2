from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)

    with app.app_context():
        db.create_all()  # Creates database tables based on models

    from .routes import workout_blueprint
    app.register_blueprint(workout_blueprint, url_prefix='/api')

    return app