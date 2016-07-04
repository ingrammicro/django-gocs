import os
import time
from setuptools import setup
from os.path import join, dirname, abspath

__version__ = '0.0'
__author__ = 'APS Lite team'


def version():
    path_version = join(dirname(abspath(__file__)), 'version.txt')

    def version_file(mode='r'):
        return open(path_version, mode)

    if os.path.exists(path_version):
        with version_file() as verfile:
            return verfile.readline().strip()

    if os.getenv('TRAVIS'):
        build_version = os.getenv('TRAVIS_BUILD_NUMBER')
    elif os.getenv('JENKINS_HOME'):
        build_version = 'jenkins{}'.format(os.getenv('BUILD_NUMBER'))
    else:
        build_version = 'dev{}'.format(int(time.time()))

    with version_file('w') as verfile:
        verfile.write('{0}.{1}'.format(__version__, build_version))

    with version_file() as verfile:
        return verfile.readline().strip()

setup(
    name='django-gocs',
    packages=['django_gocs'],
    version=version(),
    description='Django file storage backend and temporary file handler for '
                'Google Cloud Storage',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author=__author__,
    author_email='aps@odin.com',
    install_requires=[
        'django',
        'GoogleAppEngineCloudStorageClient>=1.9.15.0'
    ],
    url='https://github.com/odin-public/django-gocs',
    keywords=['django', 'storage', 'gcs', 'google cloud storage'],
    classifiers=[],
)
