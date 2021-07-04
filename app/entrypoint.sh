#!/bin/bash

set -e
shopt -s expand_aliases

function install_dependencies() {
  pip install -r /app/requirements.txt
}

function execute_development_server() {
  python manage.py runserver 0:8000
}

execute_development_server