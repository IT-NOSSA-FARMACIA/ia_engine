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
  gunicorn -c /app/gunicorn.py wsgi
}

function execute_celery() {
  if [ ${IA_ENGINE_CELERY_ON:-1} -eq 1 ]
  then
    rm /var/run/celery/*.pid
    rm /var/run/celery/celerybeat-schedule
    bash start_celery_workers.sh
    bash start_celery_beat.sh
  fi
}

function execute_web() {
  bash start_web.sh
}

if [ ${RUN_INSTALL_DEPENDENCIES:-0} -eq 1 ] ; then
  install_dependencies
fi

if [ ${IA_ENGINE_SERVICE} == "celery" ]
then
  execute_celery
else
  execute_web
fi
