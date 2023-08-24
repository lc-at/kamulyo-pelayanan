from flask_minio import Minio
from werkzeug.utils import secure_filename


class TicketAttachmentStorage:
    def __init__(self, storage, app=None):
        self._storage: Minio = storage
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        bucket_name = app.config.get('TICKET_ATTACHMENT_BUCKET_NAME')
        if not bucket_name:
            raise ValueError('TICKET_ATTACHMENT_BUCKET_NAME is not set')
        self._bucket_name = bucket_name

    @staticmethod
    def sanitize_filename(filename):
        new_filename = filename.lower()
        new_filename = secure_filename(new_filename)
        return new_filename

    def put_from_stream(self, stream, object_name):
        if not self._storage.connection:
            raise TicketAttachmentStorageException(
                'Storage connection is not set')
        return self._storage.connection.put_object(bucket_name=self._bucket_name,
                                                   object_name=object_name,
                                                   data=stream,
                                                   length=-1,
                                                   part_size=5 * 1024 * 1024)

    def get_url(self, filename):
        if not self._storage.connection:
            raise TicketAttachmentStorageException(
                'Storage connection is not set')
        return self._storage.connection.presigned_get_object(self._bucket_name, filename)


class TicketAttachmentStorageException(Exception):
    pass
