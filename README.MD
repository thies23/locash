LOCash
===

Yet another Strichlisten System

Hastly written in Python with Django Framework

# Setup

- `git clone https://github.com/thies23/locash`
- `cd locash`
- `python3 -m venv .venv`
- `source .venv/bin/activate`
- `pip3 install -r requirements.txt`
- `python3 manage.py runserver`

## Create Django Admin User
- `python3 manage.py createsuperuser`

# Features
- Select User via ID / Scan User to login
- Select Product via EAN / Scan Product to buy
- Transfer Money between Users
- Top Up Account
- Withdraw money from Account
- Reverse transaction (and undo)


# Why LOCash?
This tool was written for c3loc the logistics team of CCC events.