from flask_minio import Minio
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy

from .flask_hashids import HashidsExtension
from .flask_zenziva import ZenzivaExtension
from .ticket_attachment_storage import TicketAttachmentStorage

hashids = HashidsExtension()
zenziva = ZenzivaExtension()
db = SQLAlchemy()
storage = Minio()
ticket_attachment_storage = TicketAttachmentStorage(storage)
redis_client = FlaskRedis()
