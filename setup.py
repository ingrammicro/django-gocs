from setuptools import setup
from os.path import join, dirname

__version__ = '0.0.1'
__author__ = 'Anton Larkin'


setup(
    name='django-gocs',
    packages=['django_gocs'],
    version=__version__,
    description='Django file storage backend and temporary file handler for '
                'Google Cloud Storage',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author=__author__,
    author_email='ap-sweeft@parallels.com',
    maintainer='alarkin',
    maintainer_email='alarkin@odin.com',
    install_requires=[
        'django',
        'GoogleAppEngineCloudStorageClient==1.9.15.0'
    ],
    url='https://github.com/odin-public/django-gocs',
    keywords=['django', 'storage', 'gcs', 'google cloud storage'],
    classifiers=[],
)
