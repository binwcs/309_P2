#!/bin/bash

# create virtual environment
python3 -m venv venv

# active virtual environment
source venv/bin/activate

# install the python library
pip install -r requirements.txt

# run migration
python manage.py migrate
