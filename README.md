# codex-testing

This repository contains a minimal Flask application and a small JavaScript
widget for price calculation. The main goal of the project is to demonstrate a
simple admin interface with user authentication, basic CRUD screens and an API
that the front‑end widget can consume.

Key features:

- Management of units of measurement, service categories and individual
  services;
- Storage of application settings such as default language and currency;
- REST API used by the calculator widget to load reference data and send
  calculation results;
- A JavaScript/CSS widget located in `calculator_widget` that can be embedded in
  any site.

## Deployment

Clone the repository and enter the project directory:

```bash
git clone https://github.com/yourname/codex-testing.git
cd codex-testing
```

It is recommended to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies with pip:

```bash
pip install -r requirements.txt
```

## Environment variables

The application reads some settings from the environment:

- `SECRET_KEY` – secret value used to sign sessions. If not set, a random
  value will be generated on startup.
- `SQLALCHEMY_DATABASE_URI` – SQLAlchemy connection string. Defaults to
  `sqlite:///app.db`.
- `SMTP_SERVER` – hostname of the SMTP server. Defaults to `localhost`.
- `SMTP_PORT` – port of the SMTP server. Defaults to `25`.
- `SMTP_USERNAME` – username for SMTP authentication (optional).
- `SMTP_PASSWORD` – password for SMTP authentication (optional).
- `SMTP_USE_TLS` – set to `true` to enable TLS (optional).


Example setup:

```bash
export SECRET_KEY="change-this-key"
export SQLALCHEMY_DATABASE_URI="sqlite:///app.db"
```

## Running the application

On the first launch the application will automatically create the SQLite
database and populate it with the same default records as the `init-db`
command. This includes a user `admin` with password `admin`.

You can still initialize or reset the database manually at any time using the
CLI command:

```bash
flask --app run.py init-db
```
This command prompts before dropping any existing tables.

After the database is ready, run the development server:

```bash
python run.py
```

Once the server is running you can open the calculator widget directly at
`http://localhost:5000/calculator/`. A link to this page is also available in
the admin navigation bar.

## Database migrations

The project ships with **Flask-Migrate**. After installing the dependencies you
can create migration scripts and upgrade the database schema using the standard
Flask-Migrate commands:

```bash
flask db init      # run once to create migrations folder
flask db migrate   # generate migration scripts
flask db upgrade   # apply migrations
```

These commands use the same configuration as the application and work with the
`SQLALCHEMY_DATABASE_URI` environment variable.

## Building the widget

The static widget lives in the `calculator_widget` directory. To use it as is,
simply copy its contents to your web server. If you prefer a minified version
you can create a small build directory using Node tools:

```bash
npm install -g terser clean-css-cli
mkdir build
terser calculator_widget/calculator.js -o build/calculator.min.js
cleancss -o build/calculator.min.css calculator_widget/calculator.css
cp calculator_widget/index.html build/
```

## Running tests

After installing the dependencies, run the unit tests using `pytest`:

```bash
pytest
```
