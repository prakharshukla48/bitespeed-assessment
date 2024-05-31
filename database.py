from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    if os.environ.get('FLASK_ENV') == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://prakhar:sxlmpNyFJm9Lm18cR6ip8rGWv9FJT79x@dpg-cpcd6v0l5elc73ff3200-a.singapore-postgres.render.com/bitespeed_s884'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

