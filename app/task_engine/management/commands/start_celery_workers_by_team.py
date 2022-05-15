from django.core.management.base import BaseCommand
from task_engine.models import TeamWorker
import os


class Command(BaseCommand):
    help = "Command to run celery workers by team"

    def handle(self, *args, **options):
        team_workers = TeamWorker.objects.filter(active=True)
        for team_worker in team_workers:
            max_concurrency = team_worker.concurrency
            process_ticket_task_name = (
                f"process-ticket-{team_worker.suffix_worker_name}"
            )
            execute_schedule_task_name = (
                f"execute-schedule-{team_worker.suffix_worker_name}"
            )

            process_ticket_worker_command = f"celery multi start {process_ticket_task_name} -A ia_engine -l ERROR --autoscale={max_concurrency},1 -n %h -Q {process_ticket_task_name} --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log"
            execute_schedule_worker_command = f"celery multi start {execute_schedule_task_name} -A ia_engine -l ERROR --autoscale={max_concurrency},1 -n %h -Q {execute_schedule_task_name} --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log"

            self.stdout.write(
                f"Executing command start execute schedule for {team_worker.team.name} team"
            )
            self.stdout.write(execute_schedule_worker_command)
            os.system(execute_schedule_worker_command)
            self.stdout.write(self.style.SUCCESS("Successfully command"))

            self.stdout.write(
                f"Executing command start process ticket for {team_worker.team.name} team"
            )
            self.stdout.write(process_ticket_worker_command)
            os.system(process_ticket_worker_command)
            self.stdout.write(self.style.SUCCESS("Successfully command"))
