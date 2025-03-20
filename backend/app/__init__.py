from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
from datetime import timedelta

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:4200"}})
    
    # Configurazione del database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:password123@db/trivia?charset=utf8mb4"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600
    }
    
    # Configurazione JWT
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "super-secret-key")
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

    # Inizializzazione estensioni
    db.init_app(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)

    with app.app_context():
        from .models import User, RuoloEnum
        db.create_all()
        
        # Creazione dell'admin se non esiste
        admin_email = os.getenv('ADMIN_EMAIL', 'Admin@gmail.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'Admin123')
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                email=admin_email,
                nome='Admin',
                cognome='System',
                ruolo=RuoloEnum.admin
            )
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()

        from .routes import init_routes
        init_routes(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=3000, debug=True)
