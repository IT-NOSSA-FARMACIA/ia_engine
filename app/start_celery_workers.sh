celery multi start search-new-schedule -A ia_engine -l ERROR --concurrency=1 -n %h -Q search-new-schedule --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log
celery multi start execute-schedule -A ia_engine -l ERROR --autoscale=4,1 -n %h -Q execute-schedule --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log
celery multi start process-ticket -A ia_engine -l ERROR --autoscale=4,1 -n %h -Q process-ticket --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log
celery multi start notify-execution -A ia_engine -l ERROR --autoscale=4,1 -n %h -Q notify-execution --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log
python manage.py start_celery_workers_by_team