# Run tests and linters
@default: test lint

# Setup project
@init:
  pipenv run pip install -e '.[test,flake8,mypy]'

# Run pytest with supplied options
@test *options:
  pipenv run pytest {{options}}

# Run linters: flake8, mypy, black
@lint:
  pipenv run flake8
  pipenv run mypy hordoc tests
  pipenv run black . --check

# Apply Black
@black:
  pipenv run black .
