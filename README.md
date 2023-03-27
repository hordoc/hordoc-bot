# HorDoc: AI-Powered Discord Community Support

[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/)

Public Discord communities struggle to quickly and accurately answer user questions, especially with a constant flow of new users asking the same questions repeatedly.

HorDoc learns from previous support channel conversations to reduce the repetitive workload on community members, speed up response times, and enhance the user experience for both new and existing users seeking help in your community.

## Installation

To install and run HorDoc locally, you need at least Python 3.9 and a couple Python libraries which you can install with `pip`.

### Development build (cloning git main branch):

```bash
git clone https://github.com/hordoc/hordoc-bot.git
cd hordoc-bot
```

Recommended: Take a look at [pipenv](https://pipenv.pypa.io/). This tool provides isolated Python environments, which are more practical than installing packages systemwide. It also allows installing packages without administrator privileges.

Then install the HorDoc package (with its Python dependencies, this will take a while):
```bash
pip3 install -e .
```

Copy the example environment variables from `.env.sample` to `.env` and customize them to your needs. These include your Discord authentication token, guild, forum and channel IDs and database filename.

## Usage

Run the bot via:

```bash
python3 hordoc/bot.py
```

## Contributing
Development of HorDoc takes place in the [hordoc-bot GitHub repository](https://github.com/hordoc/hordoc-bot/).

All improvements to the software should start with an issue. Read our [Motivation for design / architecture decisions](DESIGN.md)

### Obtaining the code
To work on this library locally, first checkout the code. Then create a new virtual environment:

```bash
git clone git@github.com:hordoc/hordoc-bot
cd hordoc-bot
python3 -mvenv venv
source venv/bin/activate
```

Or if you are using pipenv:

```bash
pipenv shell
```

Within the virtual environment running `hordoc-bot` should run your locally editable version of the tool. You can use `which hordoc-bot` to confirm that you are running the version that lives in your virtual environment.

### Running the tests
To install the dependencies and test dependencies:

```bash
pip install -e '.[test]'
```

To run the tests:

```bash
pytest
```

### Linting and formatting
`hordoc-bot` uses [Black](https://black.readthedocs.io/) for code formatting, and [flake8](https://flake8.pycqa.org/) and [mypy](https://mypy.readthedocs.io/) for linting and type checking.

Black is installed as part of `pip install -e '.[test]'` - you can then format your code by running it in the root of the project:

```bash
black .
```

To install `mypy` and `flake8` run the following:

```bash
pip install -e '.[flake8,mypy]'
```
Both commands can then be run in the root of the project like this:

```bash
flake8
mypy hordoc
```

All three of these tools are run by our CI mechanism against every commit and pull request.

### Using Just and pipenv
If you install [Just](https://github.com/casey/just) and [pipenv](https://pipenv.pypa.io/) you can use them to manage your local development environment.

To create a virtual environment and install all development dependencies, run:

```bash
cd hordoc-bot
just init
```

To run all of the tests and linters:

```bash
just
```

To run tests, or run a specific test module or test by name:

```bash
just test # All tests
just test tests/test_data.py # Just this module
just test -k test_dt_to_ms # Just this test
```

To run just the linters:

```bash
just lint
```

To apply Black to your code:

```bash
just black
```

And to list all available commands:

```bash
just -l
```

## Team
[All-Ki](https://github.com/All-Ki) & [MischaU8](https://github.com/MischaU8)

This project is sponsored by the [AI Horde](https://aihorde.net/)
