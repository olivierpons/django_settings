import os
from collections.abc import Mapping
from pathlib import Path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# region - custom settings (to put in environment settings) -
class LazyDict(Mapping):
    def __init__(self, *args, **kw):
        self._raw_dict = dict(*args, **kw)

    def __getitem__(self, key):
        if key.startswith("#"):
            func, arg = self._raw_dict.__getitem__(key)
            return func(arg)
        return self._raw_dict.__getitem__(key)

    def __iter__(self):
        return iter(self._raw_dict)

    def __len__(self):
        return len(self._raw_dict)


settings = {}
errors = []


def dir_parser(error_message_if_doesnt_exist):
    return [
        str,
        lambda v: (settings["DEBUG"] is True) or Path(v).is_dir(),
        error_message_if_doesnt_exist,
    ]


def parser_array_of_str(error_message):
    return [
        eval,
        lambda tab: (
                isinstance(tab, list) and all([isinstance(x, str) for x in tab])
        ),
        error_message,
    ]  # ! array of str


def parser_url(error_message):
    def is_valid_url(url: str):
        try:
            URLValidator()(url)
        except ValidationError:
            return False
        return True

    return [
        str,
        lambda v: (isinstance(v, str) and is_valid_url(v)),
        error_message,
    ]  # ! array of str


def conf_ignore_if_sqlite():
    return {
        "default": "None",
        "parser": [
            eval,
            lambda v: (
                    (isinstance(v, str) and v != "")
                    or (v is None and "sqlite" in settings["DATABASE_ENGINE"])
            ),
            "Your database isn't sqlite, this var must be configured",
        ],
    }


environment_variables = LazyDict(
    {
        # SECURITY WARNING: don't run with debug turned on in production!
        "DEBUG": {
            "required": True,
            "parser": [eval, lambda v: isinstance(v, bool)],
        },
        "SECRET_KEY": {"required": True},
        "MEDIA_ROOT": {"default": "uploads"},
        "STATIC_ROOT": {
            "default": "../production_static_files",
            "parser": dir_parser("Production folder doesn't exist."),
        },
        "COMPRESS_ROOT": {
            "default": "../production_static_files/compress",
            "parser": dir_parser("Compress production folder doesn't exist."),
        },
        # when set to None = no limit to be able to send huge amount of data:
        "DATA_UPLOAD_MAX_NUMBER_FIELDS": {
            "required": True,
            "parser": [eval, lambda v: v is None or isinstance(v, int)],
        },
        # for uploads
        "UPLOAD_FOLDER_DOCUMENTS": {"default": "documents"},
        "UPLOAD_FOLDER_CHATS_DOCUMENT": {"default": "chats/documents"},
        "UPLOAD_FOLDER_IMAGES": {"default": "images"},
        "THUMBNAIL_SUBDIRECTORY": {"default": "th"},
        "THUMBNAIL_DIMENSIONS": {
            "default": "(1125, 2436)",  # iPhone X resolution
            "parser": [eval, lambda v: (type(v) is tuple) and len(v) == 2],
        },
        # https://docs.djangoproject.com/en/dev/ref/settings/
        "ALLOWED_HOSTS": {
            "default": "[]",
            "required": True,  # default = no hosts
            "parser": parser_array_of_str("ALLOWED_HOSTS = list of str only!"),
        },
        "INTERNAL_IPS": {
            "default": '["127.0.0.1", ]',
            "required": True,
            "parser": parser_array_of_str("INTERNAL_IPS = list of str only!"),
        },
        "LOCALE_PATHS": {  # default path for locale is 'base_dir/locale':
            "default": "(os.path.join(BASE_DIR, 'locale'), )",
            "parser": [eval, lambda v: (type(v) is tuple)],
        },
        # DATABASE_ENGINE = 'django.db.backends.postgresql_psycopg2' :
        "DATABASE_ENGINE": {"default": "django.db.backends.sqlite3"},
        "DATABASE_NAME": {"default": os.path.join(BASE_DIR, "db.sqlite3")},
        "DATABASE_HOST": conf_ignore_if_sqlite(),
        "DATABASE_CLIENT_ENCODING": conf_ignore_if_sqlite(),
        "DATABASE_DATABASE": conf_ignore_if_sqlite(),
        "DATABASE_USER": conf_ignore_if_sqlite(),
        "DATABASE_PASSWORD": conf_ignore_if_sqlite(),

    }
)


def parse_var(p_var, p_infos):
    global settings
    if p_var in os.environ:
        settings[p_var] = os.environ[p_var]
    elif "default" in p_infos:
        settings[p_var] = p_infos["default"]
    elif "required" in p_infos:
        errors.append(p_var)
        return
    if "parser" in p_infos:
        parser = p_infos["parser"]
        if p_var not in settings:
            raise Exception(
                f"{p_var}: variable not set in environment, and "
                "has not 'default' or 'required' value"
            )
        # ! parser functions: 0 = convert, 1 = validate conversion, 2 = error:
        try:
            settings[p_var] = parser[0](settings[p_var])
        except TypeError:
            raise Exception(f"{p_var}: conversion error using {parser[0]}")

        if not parser[1](settings[p_var]):  # should not continue -> exception:
            if len(parser) > 2:
                raise Exception(f"var: {p_var}: {parser[2]}")
            raise Exception(f"Unexpected conversion for variable '{p_var}'")


# first parse debug then *AFTER* parse all other variables
for var, infos in environment_variables.items():
    if var == "DEBUG":
        parse_var(var, infos)

for var, infos in environment_variables.items():
    if var != "DEBUG":
        parse_var(var, infos)

if len(errors):
    raise Exception(
        "Please set the environment variables: " "{}.".format(", ".join(errors))
    )

# endregion - custom settings (to put in environment settings) -

MEDIA_ROOT = settings["MEDIA_ROOT"]
COMPRESS_ROOT = settings["COMPRESS_ROOT"]
SECRET_KEY = settings["SECRET_KEY"]
DEBUG = settings["DEBUG"]
DATA_UPLOAD_MAX_NUMBER_FIELDS = settings["DATA_UPLOAD_MAX_NUMBER_FIELDS"]
UPLOAD_FOLDER_DOCUMENTS = settings["UPLOAD_FOLDER_DOCUMENTS"]
UPLOAD_FOLDER_CHATS_DOCUMENT = settings["UPLOAD_FOLDER_CHATS_DOCUMENT"]
UPLOAD_FOLDER_IMAGES = settings["UPLOAD_FOLDER_IMAGES"]
THUMBNAIL_SUBDIRECTORY = settings["THUMBNAIL_SUBDIRECTORY"]
THUMBNAIL_DIMENSIONS = settings["THUMBNAIL_DIMENSIONS"]
ALLOWED_HOSTS = settings["ALLOWED_HOSTS"]
INTERNAL_IPS = settings["INTERNAL_IPS"]
STATIC_ROOT = settings["STATIC_ROOT"]
LOCALE_PATHS = settings["LOCALE_PATHS"]
