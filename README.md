# codex-testing

This repository contains a minimal Flask application.

## Installation

It is recommended to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies with pip:

```bash
pip install -r requirements.txt
```

## Running the application

Initialize the database with default data using the provided CLI command:

```bash
flask --app run.py init-db
```

Then run the development server:

```bash
python run.py
```

