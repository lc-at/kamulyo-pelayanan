from flask_migrate import Migrate
from flask_minio import Minio
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy

from .flask_hashids import HashidsExtension
from .flask_zenziva import ZenzivaExtension
from .ticket_attachment_storage import TicketAttachmentStorage

db = SQLAlchemy()
hashids = HashidsExtension()
migrate = Migrate()
redis_client = FlaskRedis()
storage = Minio()
ticket_attachment_storage = TicketAttachmentStorage(storage)
zenziva = ZenzivaExtension()
