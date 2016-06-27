"""
Google Cloud Storage file backend and temporary handler for Django
"""

import os
import errno
import mimetypes

from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.utils.deconstruct import deconstructible
from django.utils.crypto import get_random_string

try:
    import cloudstorage as gcs
except ImportError:
    pass


class GoogleBlobstoreTemporaryUploadedFile(TemporaryUploadedFile):

    def __init__(self, name, content_type, size, charset,
                 content_type_extra=None):
        file_name = '{}/{}.upload'.format(
            settings.GOOGLE_CLOUD_STORAGE_BUCKET_TEMP,
            name
        )

        while self.exists(file_name):
            file_name = file_name + get_random_string(7)

        file = gcs.open(file_name, 'w')
        super(TemporaryUploadedFile, self).__init__(
            file, name, content_type, size, charset, content_type_extra)

    def close(self, delete=True):
        try:
            if delete:
                gcs.delete(self.file.name)
        except gcs.NotFoundError:
            pass

        try:
            return self.file.close()
        except OSError as e:
            if e.errno != errno.ENOENT:
                # Means the file was moved or deleted before the tempfile
                # could unlink it.  Still sets self.file.close_called and
                # calls self.file.file.close() before the exception
                raise

    def exists(self, name):
        try:
            gcs.stat(name)
            return True
        except gcs.NotFoundError:
            return False


class GoogleBlobstoreTemporaryFileUploadHandler(TemporaryFileUploadHandler):

    def new_file(self, file_name, *args, **kwargs):
        super(TemporaryFileUploadHandler, self).new_file(
            file_name, *args, **kwargs)
        self.file = GoogleBlobstoreTemporaryUploadedFile(
            self.file_name, self.content_type, 0, self.charset,
            self.content_type_extra
        )

    def file_complete(self, file_size):
        self.file.size = file_size

        # close StreamingBuffer and open ReadBuffer
        self.file.close(delete=False)
        self.file.file = gcs.open(self.file.file.name, 'r')

        return self.file


@deconstructible
class GoogleCloudStorage(Storage):
    def __init__(self, location=None, base_url=None):
        if location is None:
            location = settings.GOOGLE_CLOUD_STORAGE_BUCKET
        self.location = location
        if base_url is None:
            base_url = settings.GOOGLE_CLOUD_STORAGE_URL
        self.base_url = base_url

    def _open(self, name, mode='r'):
        filename = self.location + "/" + name

        # rb is not supported
        if mode == 'rb':
            mode = 'r'

        if mode == 'w':
            type, encoding = mimetypes.guess_type(name)
            cache_control = settings.GOOGLE_CLOUD_STORAGE_DEFAULT_CACHE_CONTROL
            gcs_file = gcs.open(filename, mode=mode, content_type=type,
                                options={'x-goog-acl': 'public-read',
                                         'cache-control': cache_control})
        else:
            gcs_file = gcs.open(filename, mode=mode)

        return gcs_file

    def _save(self, name, content):
        filename = self.location + "/" + name
        filename = os.path.normpath(filename)
        type, encoding = mimetypes.guess_type(name)
        cache_control = settings.GOOGLE_CLOUD_STORAGE_DEFAULT_CACHE_CONTROL

        # Files are stored with public-read permissions.
        # Check out the google acl options if you need to alter this.
        gss_file = gcs.open(filename, mode='w', content_type=type,
                            options={'x-goog-acl': 'public-read',
                                     'cache-control': cache_control})

        try:
            content.open()
        except:
            pass

        for chunk in content.chunks():
            gss_file.write(chunk)

        try:
            content.close()
        except:
            pass

        gss_file.close()
        return name

    def delete(self, name):
        filename = self.location+"/"+name
        try:
            gcs.delete(filename)
        except gcs.NotFoundError:
            pass

    def exists(self, name):
        try:
            self.statFile(name)
            return True
        except gcs.NotFoundError:
            return False

    def listdir(self, path=None):
        directories, files = [], []
        bucketContents = gcs.listbucket(self.location, prefix=path)
        for entry in bucketContents:
            filePath = entry.filename
            head, tail = os.path.split(filePath)
            subPath = os.path.join(self.location, path)
            head = head.replace(subPath, '', 1)
            if head == "":
                head = None
            if not head and tail:
                files.append(tail)
            if head:
                if not head.startswith("/"):
                    head = "/" + head
                dir = head.split("/")[1]
                if dir not in directories:
                    directories.append(dir)
        return directories, files

    def size(self, name):
        stats = self.statFile(name)
        return stats.st_size

    def accessed_time(self, name):
        raise NotImplementedError

    def created_time(self, name):
        stats = self.statFile(name)
        return stats.st_ctime

    def modified_time(self, name):
        return self.created_time(name)

    def url(self, name):
        server_software = os.getenv("SERVER_SOFTWARE", "")
        if not server_software.startswith("Google App Engine"):
            # we need this in order to display images, links to files, etc
            # from the local appengine server
            from google.appengine.api.blobstore import create_gs_key

            filename = "/gs" + self.location + "/" + name
            key = create_gs_key(filename)
            local_base_url = getattr(settings, "GOOGLE_CLOUD_STORAGE_DEV_URL",
                                     "http://localhost:8001/blobstore/blob/")
            return local_base_url + key + "?display=inline"
        return self.base_url + "/" + name

    def statFile(self, name):
        filename = self.location + "/" + name
        return gcs.stat(filename)
