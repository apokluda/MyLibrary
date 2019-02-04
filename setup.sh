#!/bin/bash

echo "Runing apt update"
sudo apt update

echo "Installing python-pip"
sudo apt install python-pip

echo "Installing virtualenv"
pip install virtualenv

echo "Creating virtualenv in directory .venv"
virtualenv -p /usr/bin/python3 .venv

echo "Activating virtualenv"
source .venv/bin/activate

echo "Installing dependencies..."
pip install falcon
pip install peewee
pip install jsonschema
pip install pytest
pip install falcon-auth
pip install gunicorn
pip install httpie
