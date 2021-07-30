#!/bin/bash

set -e
shopt -s expand_aliases

cd "/app"

function install_dependencies() {
  pip install -r /app/requirements.txt
}

function execute_development_server() {
  python manage.py runserver 0:8000
}

function run_collectstatic() {
  python manage.py collectstatic --noinput
}

function execute_gunicorn() {
  echo " executing gunicorn"
  gunicorn ia_engine.asgi:application -b :8000 -w 4 -k uvicorn.workers.UvicornWorker --log-file -
  echo "finish executing gunicorn"
}

case ${IA_ENGINE_SERVICE:-development} in
production)
  if [ ${RUN_COLLECT_STATIC:-0} -eq 1 ]; then
    run_collectstatic
  fi
  if [ ${RUN_INSTALL_DEPENDENCIES:-0} -eq 1 ]; then
    install_dependencies
  fi
  execute_gunicorn
  ;;
development)
  execute_development_server
  ;;
*)
  echo "Sorry, an error occurred"
  ;;
esac
