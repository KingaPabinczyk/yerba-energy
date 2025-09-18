from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "supersecretkey"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../data/mini_shop.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)   

    from .routes import bp
    app.register_blueprint(bp)

    with app.app_context():
        from .models import User
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                role="admin",
                first_name="Admin",
                last_name="User",
                street="Testowa",
                house_number="1",
                postal_code="00-000",
                city="Nowhere",
                email="admin@example.com"
            )
            admin.set_password("admin")
            db.session.add(admin)
            db.session.commit()


    return app

