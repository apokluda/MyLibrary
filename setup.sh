#!/bin/bash

sudo apt update
sudo apt install python-pip
pip install virtualenv
virtualenv -p /usr/bin/python3 .venv
source .venv/bin/activate
pip install falcon peewee jsonschema pytest falcon-auth
pip install gunicorn httpie
