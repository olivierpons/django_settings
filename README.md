# Django settings
A base settings easy to read, easy to use, while keeping
100% of the [JetBrains/PyCharm][2] features (eg. auto-completion).

## Development / production howto with `settings.py` (summary)
After many websites development with Django, you will probably come up with
a solution to setup your development and your production settings.

You have to keep your `settings.py` in your repositories because 
it's often needed. They will be different between development and production. 
This will be a problem when you'll try to update your production 
using your development code. 

The basic principle is to set a variable in your environment, and in the
`settings.py`, just read the variable, like, for example:
```python
import os

DEBUG = os.environ['DEBUG']
```

Easy. But when you have tons of variables, and for each variable, you
need to check:

- if it's set in the environment. If not, raise an Exception = not continue
- if what's in the variable is *exactly what you expect* (type checking, maybe
more).

To solve this, there are many approaches.

There are some useful tools like [`django-configurations`][1]

But if you work with [PyCharm][2], one of its biggest help is the
auto-completion feature. Time gained. Efficiency.
But if you use the previous tool:

- you won't instant access to your variable declarations anymore (Ctrl-click)
- no more possibilities to call auto-completion features
 
That there are **no** "Django settings" libraries available that 
will keep PyCharm *"aware"* of all your settings variables
(if you know one let me know, I'm interested!).

... On the other side, if you want to keep your settings very simple (e.g.
like you have when you start a new Django project), you won't be able to 
easily switch between development and production environments.   


## django_settings: in the middle of two worlds. 
That's why I wrote `django_settings`:
- to use the environment variables to setup the configuration
- to make sure what's in the variable is *exactly what you expect*
- to stay 100% compatible with `PyCharm`


This is why you still have a few things to do, but **far less to do**
than with "basic" Django settings file, and you won't loose your `PyCharm`
auto-completion and variable settings features.

## django_settings: howto 
- Copy/paste the code of the settings file `settings.py` in this repo here
  **at the beginning** of your own `settings.py` file.
- comment all your variables that are declared *after* this code. `PyCharm`
  is here to help: you will see PyCharm's suggestion like
  "`Redeclared 'YOUR_CONST' defined above without usage`".
- and setup your environment variables: in Linux, there are many ways to
  setup your environment variables, the easiest one to test is to type
  your assignments and then execute your command, for example:
```python
DEBUG='True' python3 manage.py runserver
```

And you will see `settings.py` in action: if all the required environment
variables are here everything will work flawlessly, otherwise your will
read something like:

```python
  File "/home/hqf-development/projects/my_project/settings.py", line 100, in <module>
    raise Exception("Please set the environment variables: "
Exception: Please set the environment variables: DATA_UPLOAD_MAX_NUMBER_FIELDS.
```

... and you will know which variable is missing.

- If you want to setup everything in [`PyCharm`][2] just add a new
configuration (button "Add Configuration" on the top right of 
[`PyCharm`][2]), and just change your environment variables in this
setting.

## How to handle sqlite/development and PostGreSQL/production settings?
You have nothing to do with this `settings.py` code: the function
`conf_ignore_if_sqlite()` will use what you've setup in your environment
variable and if you are in development mode (= `DEBUG='True'`) it supposes
you use sqlite. You might change the code to meet your requirements.

If you use PostGreSQL in production, when you set `DEBUG='False'` in
your environment variables, the code I've done makes sure you have
all other environment variables set (`DATABASE_USER`, `DATABASE_PASSWORD`
etc.).

## How to add new variable in this settings?

### Suppose you need to add new variable called `SMS_PRO_SECRET_KEY`.

Go to the last value of the environment dictionary  
`environment_variables = {}`, and add a new key with a new value,
for example:

```python
environment_variables = {
   # other key/values.. until the last one:
   'SMS_PRO_SECRET_KEY': {'default': 'Mysecret key'},
}
```
Then after all the variables declaration, add yours: like:

```
SMS_PRO_SECRET_KEY = settings['SMS_PRO_SECRET_KEY']
```

And you're good to go!

### What if you need to make sure `SMS_PRO_SECRET_KEY` is of a specific type?
Precise what the parser is, and a callback function that checks if
it is of the expected type.

Example:

```python
environment_variables = {
   # other key/values.. until the last one:
    'SMS_PRO_SECRET_KEY': {
        'default': 'Mysecret key',
        'parser': [eval, lambda v: isinstance(v, str) and v != '']},
}
```

There's one accepted third value in the array of the `'parser'` option:
the error string that is raised if the environment variable doesn't fit
with the requirements.

Example:

```python
environment_variables = {
   # other key/values.. until the last one:
    'SMS_PRO_SECRET_KEY': {
        'default': 'Mysecret key',
        'parser': [eval, lambda v: isinstance(v, str) and v != '',
        "The SMS secret key must be a non-empty string"]},
}
```

If you find this `settings.py` useful let me know! 

[1]: https://django-configurations.readthedocs.io/en/stable/`django-configurations` 
[2]: https://www.jetbrains.com/pycharm/