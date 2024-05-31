from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def init_db(app):
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL_PROD')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

