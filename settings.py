import os
from pathlib import Path

from django.urls import reverse_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# region - custom settings (to put in environment settings) -
settings = {}
errors = []


def str_parser(error_message_if_doesnt_exist):
    return [str, lambda v: (settings['DEBUG'] is True) or Path(v).is_dir(),
            error_message_if_doesnt_exist]


def conf_ignore_if_sqlite():
    return {
        'default': 'None',
        'parser': [eval,
                   lambda v:
                   (isinstance(v, str) and v != '') or
                   (v is None and 'sqlite' in settings['DATABASE_ENGINE']),
                   "Your database isn't sqlite, this var must be configured"]}


environment_variables = {
    # SECURITY WARNING: don't run with debug turned on in production!
    'DEBUG': {'required': True,
              'parser': [eval, lambda v: isinstance(v, bool)]},
    'SECRET_KEY': {'required': True, },
    'MEDIA_ROOT': {'default': 'uploads'},
    'STATIC_ROOT': {
        'default': '../production_static_files',
        'parser': str_parser("Production folder doesn't exist.")},
    'COMPRESS_ROOT': {
        'default': '../production_static_files/compress',
        'parser': str_parser("Compress production folder doesn't exist.")},
    # when set to None = no limit to be able to send huge amount of data:
    'DATA_UPLOAD_MAX_NUMBER_FIELDS': {
        'required': True,
        'parser': [eval, lambda v: v is None or isinstance(v, int)]},
    # for uploads
    'UPLOAD_FOLDER_DOCUMENTS': {'default': 'documents'},
    'UPLOAD_FOLDER_CHATS_DOCUMENT': {'default': 'chats/documents'},
    'UPLOAD_FOLDER_IMAGES': {'default': 'images'},
    'THUMBNAIL_SUBDIRECTORY': {'default': 'th'},
    'THUMBNAIL_DIMENSIONS': {
        'default': '(1125, 2436)',  # iPhone X resolution
        'parser': [eval, lambda v: (type(v) is tuple) and len(v) == 2]},
    'ALLOWED_HOSTS': {
        'default': '[]', 'required': True,  # default = no hosts
        'parser': [eval,
                   lambda tab: isinstance(tab, list) and all([
                       isinstance(x, str) for x in tab])]},  # ! array of str

    # DATABASE_ENGINE = 'django.db.backends.postgresql_psycopg2' :
    # 'ENGINE': 'django.db.backends.sqlite3',
    # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    'DATABASE_ENGINE': {'default': 'django.db.backends.sqlite3', },
    'DATABASE_NAME': {'default': os.path.join(BASE_DIR, 'db.sqlite3'), },

    'DATABASE_HOST': conf_ignore_if_sqlite(),
    'DATABASE_CLIENT_ENCODING': conf_ignore_if_sqlite(),
    'DATABASE_DATABASE': conf_ignore_if_sqlite(),
    'DATABASE_USER': conf_ignore_if_sqlite(),
    'DATABASE_PASSWORD': conf_ignore_if_sqlite(),
}

for var, infos in environment_variables.items():
    if var in os.environ:
        settings[var] = os.environ[var]
    elif 'default' in infos:
        settings[var] = infos['default']
    elif 'required' in infos:
        errors.append(var)
        continue
    if 'parser' in infos:
        parser = infos['parser']
        if var not in settings:
            raise Exception(f"{var}: variable not set in environment, and "
                            "has not 'default' or 'required' value")
        # ! parser functions: 0 = convert, 1 = validate conversion, 2 = error:
        try:
            settings[var] = parser[0](settings[var])
        except TypeError:
            raise Exception(f"{var}: conversion error using {parser[0]}")
        if not parser[1](settings[var]):  # should not continue -> exception:
            if len(parser) > 2:
                raise Exception(f'{var=} : {parser[2]}')
            raise Exception(f'Unexpected conversion for variable {var}')

if len(errors):
    raise Exception("Please set the environment variables: "
                    "{}.".format(', '.join(errors)))

MEDIA_ROOT = settings['MEDIA_ROOT']
COMPRESS_ROOT = settings['COMPRESS_ROOT']
SECRET_KEY = settings['SECRET_KEY']
DEBUG = settings['DEBUG']
DATA_UPLOAD_MAX_NUMBER_FIELDS = settings['DATA_UPLOAD_MAX_NUMBER_FIELDS']
UPLOAD_FOLDER_DOCUMENTS = settings['UPLOAD_FOLDER_DOCUMENTS']
UPLOAD_FOLDER_CHATS_DOCUMENT = settings['UPLOAD_FOLDER_CHATS_DOCUMENT']
UPLOAD_FOLDER_IMAGES = settings['UPLOAD_FOLDER_IMAGES']
THUMBNAIL_SUBDIRECTORY = settings['THUMBNAIL_SUBDIRECTORY']
THUMBNAIL_DIMENSIONS = settings['THUMBNAIL_DIMENSIONS']
ALLOWED_HOSTS = settings['ALLOWED_HOSTS']
STATIC_ROOT = settings['STATIC_ROOT']

# endregion - custom settings (to put in environment settings) -