
Quickstart
----------

First, clone the project on your local machine: ::

    https://github.com/decapolis-dfg/decapolis-parser.git
Then activate poetry by typing: ::

    poetry shell
If the poetry not installed, install it before implementing the previous command: ::

    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -
    export PATH="$HOME/.poetry/bin:$PATH"
    poetry install
    poetry shell

Then create ``.env`` file and fill it by the following variables ::

    DB_ENGINE=postgresql
    DB_NAME=#DON'T Forget to set this value
    DB_USERNAME=#DON'T Forget to set this value
    DB_PASSWORD=#DON'T Forget to set this value
    DB_HOST=localhost
    DB_PORT=5432
    ENVIRONMENT=local
Then run the migration files use::

    alembic upgrade head
Finally to run the app::

    uvicorn app.main:app --reload
    or

    uvicorn app.main:app --reload --port {PORT_NUMBER}


**Congratulations the service is working now**



Very Important Notes
----------
**1- Frequently we find issues with migrations and this blocked services to be deployed.**



please consider the below points to avoid these issues:
please try to keep these notes in your mind

- All Development must be done on local DB, not on AWS DB

- Please don't run the "alembic upgrade head" while connecting to AWS database, for testing you can run this command on your local machine only.

- Make sure to run an auto-generate command after any small/large edit on models.

- Make sure to run the alembic upgrade head command after every migration file generation.

- Don't remove any executed migration file.

- Don't edit any executed migration file.

- Also don’t forget to add each model you build, to the model’s __init__.py file to allow auto-generation of migration fiels.

2- **Don't change the value of environment variable ENVIRONMENT, Keep it "local" always**



API documentation
----------

All APIs are available on ``{{base_url}}/users/docs`` or ``{{base_url}}/users/redoc`` paths with Swagger or ReDoc.



