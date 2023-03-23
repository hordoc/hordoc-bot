# HorDoc: AI-Powered Discord Community Support

[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/)

Public Discord communities struggle to quickly and accurately answer user questions, especially with a constant flow of new users asking the same questions repeatedly.

HorDoc learns from previous support channel conversations to reduce the repetitive workload on community members, speed up response times, and enhance the user experience for both new and existing users seeking help in your community.

## Team
[All-Ki](https://github.com/All-Ki) & [MischaU8](https://github.com/MischaU8)

This project is sponsored by the [AI Horde](https://aihorde.net/)

## Installation

To install and run HorDoc locally, you need at least Python 3.9 and a couple Python libraries which you can install with `pip`.

### Development build (cloning git main branch):

```bash
git clone https://github.com/hordoc/hordoc-bot.git
cd hordoc-bot
```

Recommended: Take a look at [pipenv](https://pipenv.pypa.io/). This tool provides isolated Python environments, which are more practical than installing packages systemwide. It also allows installing packages without administrator privileges.

Install the Python dependencies, this will take a while:

```bash
pip3 install -r requirements.txt
```

Copy the example environment variables from `.env.sample` to `.env` and customize them to your needs. These include your Discord authentication token, guild, forum and channel IDs and database filename.

## Usage

Run the bot via:

```bash
./bot.py
```

## Design

Read our [Motivation for design / architecture decisions](DESIGN.md)
