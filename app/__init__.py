from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Login in to see this site.'
    login_manager.login_message_category = 'warning'

    from app import models

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    from app.routes import main
    app.register_blueprint(main)

    from app.auth import auth
    app.register_blueprint(auth)

    from app.transactions import transactions_bp
    app.register_blueprint(transactions_bp)

    with app.app_context():
        db.create_all()
        
        from app.models import Category
        if Category.query.count() == 0:
            default_categories = [
                Category(name='Food & Drinks', color='#e74c3c', icon='🍔'),
                Category(name='Transport', color='#3498db', icon='🚗'),
                Category(name='Housing', color='#2ecc71', icon='🏠'),
                Category(name='Entertainment', color='#9b59b6', icon='🎮'),
                Category(name='Health', color='#1abc9c', icon='💊'),
                Category(name='Clothing', color='#e67e22', icon='👕'),
                Category(name='Savings', color='#f1c40f', icon='💰'),
                Category(name='Other', color='#95a5a6', icon='📦'),
            ]
            db.session.add_all(default_categories)
            db.session.commit()

    from app.budgets import budgets_bp
    app.register_blueprint(budgets_bp)

    return app