from flask import Flask, request, current_app
from sqlalchemy import schema
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
# from flask_uploads import UploadSet, configure_uploads, IMAGES
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from contextlib import contextmanager
# from flask_sqlalchemy_session import flask_scoped_session


from sqlalchemy.orm import sessionmaker

# engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
# session_factory = sessionmaker(bind=engine)

oracle_schema = 'C##SHOP_USER'
oracle_db_metadata = schema.MetaData(schema=oracle_schema)
db = SQLAlchemy(metadata=oracle_db_metadata)

class DBSession:
    store = {}

views = []

migrate = Migrate()
socketio = SocketIO()
jwt = JWTManager()

@contextmanager
def db_session():
    # return db.create_scoped_session(options=dict(bind=db.get_engine(current_app._get_current_object()), binds={}))
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, convert_unicode=True)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # connection = engine.connect()
    db_session = scoped_session(session_factory)
    yield db_session
    db_session.close()
    # connection.close()

def register_blueprints(app):
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth/')

    from app.product import bp as product_bp
    app.register_blueprint(product_bp, url_prefix='/product/')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    migrate.init_app(app, db)
    socketio.init_app(app, message_queue="redis://")
    jwt.init_app(app)

    register_blueprints(app)
    # configure_uploads(app, (avatar,))

    app.app_context().push()
    return app
