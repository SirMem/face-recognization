"""Initialize all Flask extensions."""

from flask_jwt_extended import JWTManager
from flask_smorest import Api
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
api = Api()
ma = Marshmallow()
limiter = Limiter(key_func=get_remote_address)
