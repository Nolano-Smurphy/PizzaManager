# Pizza Manager
By: Nolan Murphy

### Version Requirements
This project was built Python 3.12.0 and Django 5.0.2, however, it will run on Python 3.10.5 or any version of Python which supports Django 5.0.2.

### Building Local Pizza Manager

The server can be run using gunicorn by running the following command in the working directory (PizzaShop) on the same level that contains `manage.py`:
```
gunicorn PizzaShop.wsgi --bind 127.0.0.1:8000
```
The bind tag is optional but any IP Address and Port Number are accepted. If left out, the webserver will default to `127.0.0.1:8000` as the place to listen for requests to.

Alternatively, the server can be run using Django's development server by running this command on the same level that contains `manage.py`:
```
python manage.py runserver 127.0.0.1:8000
```
Simlar to the bind tag with gunicorn, any IP Adress and Port Number are accepted.

#### Note If Not Running Off Default Host
If you plan to run the local server on a host other than localhost, you will need to add the host name to the `ALLOWED_HOSTS` field in `PizzaShop/settings.py`.

#### Disabling DEBUG Mode
If you wish to disable DEBUG mode while running the local server, go to the working directory and set the DJANGO_DEBUG environment variable to "False":

On Mac/Linux:
```
export DJANGO_DEBUG='False'
```

On Windows:
```
set DJANGO_DEBUG='False'
```

### Running Local Pizza Manager Tests
Tests can be run on the server by running the following command in the working directory (PizzaShop) on the same level that contains `manage.py`:
```
python manage.py test PizzaManager/tests
```
If you decide to relocate the tests folder from it's default location, the final argument will need to be replaced with an updated path to the new location of the tests folder. This command follows the usual Django method of identifying which files are test files (which can be found here: https://docs.djangoproject.com/en/5.0/topics/testing/overview/).
