django-gocs
===========================
[![Build Status](https://travis-ci.org/odin-public/django-gocs.svg?branch=master)](https://travis-ci.org/odin-public/django-gocs)
Google Cloud Storage file backend for Django

If you run your projects on Google's appengine and you are using the django framework you might need this
file backend since there is no way to upload files, images, etc on appengine.
Also downloadable files should use the memory to fully load before being stored in the bucket, because they
can't use temporary files in gae.

Prerequisites
-------------

You need to have an appengine project. This will not work as a standalone solution for non appengine django projects, since there is no authentication mechanism with the google cloud storage implemented.


### If you want to copy the files into your repository.

You need to install the GCS client library from
https://developers.google.com/appengine/docs/python/googlecloudstorageclient/download.

Just run `pip install GoogleAppEngineCloudStorageClient -t <your_app_directory/lib>`, or optionally, unzip the file and copy the `src/cloudstorage` folder into your project directory.

Installation
-------------

```
pip install django-gocs
```

Or Just copy the google folder in your project directory

Configuration
-------------

On your django settings.py file you need to add the following settings

    GOOGLE_CLOUD_STORAGE_BUCKET = '/your_bucket_name' # the name of the bucket you have created from the google cloud storage console
    GOOGLE_CLOUD_STORAGE_BUCKET_TEMP = '/your_temp_bucket_name' # bucket for temporary files
    GOOGLE_CLOUD_STORAGE_URL = 'http://storage.googleapis.com/bucket' #whatever the ulr for accessing your cloud storgage bucket
    GOOGLE_CLOUD_STORAGE_DEFAULT_CACHE_CONTROL = 'public, max-age: 7200' # default cache control headers for your files

And finally declare the file storage backend you will use on your settings.py file

    DEFAULT_FILE_STORAGE = 'django_gocs.GoogleCloudStorage'

    FILE_UPLOAD_HANDLERS = (
        'django.core.files.uploadhandler.MemoryFileUploadHandler',
        'django_gocs.GoogleBlobstoreTemporaryFileUploadHandler',
    )
