# Run tests and linters
@default: test lint

# Setup project
@init:
  pipenv run pip install -e '.[test,flake8,mypy]'

# Run pytest with supplied options
@test *options:
  pipenv run pytest {{options}}

# Run linters: black, flake8, mypy
@lint:
  pipenv run black . --check
  pipenv run flake8
  pipenv run mypy hordoc tests

# Apply Black
@black:
  pipenv run black .
