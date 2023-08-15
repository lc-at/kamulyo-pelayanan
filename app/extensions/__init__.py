from .flask_hashids import HashidsExtension
from .flask_zenziva import ZenzivaExtension
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy

hashids = HashidsExtension()
zenziva = ZenzivaExtension()
db = SQLAlchemy()
redis_client = FlaskRedis()
