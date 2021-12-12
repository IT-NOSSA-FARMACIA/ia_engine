from .choices import (
    EXECUTION_STATUS_SUCCESS,
    EXECUTION_STATUS_ERROR,
    NOTIFICATION_TYPE_NEVER,
    NOTIFICATION_TYPE_ERROR,
    NOTIFICATION_TYPE_SUCCESS,
    NOTIFICATION_TYPE_ALL,
)

from .models import ScheduleExecution, Ticket

from .exceptions import ParametersNotFound
from django.conf import settings

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from typing import List

import smtplib


class Notification:
    def __init__(self):
        self._status_mapping = {
            NOTIFICATION_TYPE_SUCCESS: [EXECUTION_STATUS_SUCCESS],
            NOTIFICATION_TYPE_ERROR: [EXECUTION_STATUS_ERROR],
            NOTIFICATION_TYPE_ALL: [EXECUTION_STATUS_SUCCESS, EXECUTION_STATUS_ERROR],
            NOTIFICATION_TYPE_NEVER: [],
        }

        self.notification_subject = (
            "Notificação de automação - Status {execution_status}"
        )
        self.notification_body = "Olá,<br><br>Conforme cadastro, a sua automação '{schedule_name}' \
                                  foi executado e se encontra \
                                  com o status {execution_status}.<br>\
                                  Por favor, <a href={execution_link}>clique aqui para verificar a execução.</a>\
                                  <br><br>Atenciosamente,<br>Equipe IA Engine "
        self.ia_engine_host = settings.IA_ENGINE_HOST

    def _get_execution_status_pe_notification_type(
        self, notification_type: str
    ) -> List[str]:
        return self._status_mapping.get(notification_type, [])

    def is_to_notify(self, notification_type: str, execution_status: str) -> bool:
        mapping_execution_status = self._get_execution_status_pe_notification_type(
            notification_type
        )
        return execution_status in mapping_execution_status

    def notify(
        self, schedule_execution: ScheduleExecution = None, ticket: Ticket = None
    ) -> None:
        if ticket:
            execution_status = ticket.get_execution_status_display()
            execution_link = (
                self.ia_engine_host + f"task_engine/ticket/{ticket.id}"
            )
            schedule = ticket.schedule
        elif schedule_execution:
            schedule = schedule_execution.schedule
            execution_status = schedule_execution.get_execution_status_display()
            execution_link = (
                self.ia_engine_host
                + f"task_engine/schedule/execution/{schedule_execution.id}"
            )
        else:
            raise ParametersNotFound("schedule_execution or ticket is mandatory")

        subject = self.notification_subject.format(execution_status=execution_status)
        body = self.notification_body.format(
            execution_status=execution_status,
            execution_link=execution_link,
            schedule_name=schedule.name,
        )

        from_addr = settings.FROM_EMAIL_NOTIFICATION
        to_addr = schedule.emails_to_notification
        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))
        smtp_host, smtp_port = settings.SMTP_HOST_EMAIL_NOTIFICATION.split(":")
        server = smtplib.SMTP(host=smtp_host, port=int(smtp_port))

        if settings.PASSWORD_EMAIL_NOTIFICATION:
            server.starttls()
            password = settings.PASSWORD_EMAIL_NOTIFICATION
            server.login(from_addr, password)

        text = msg.as_string()
        server.sendmail(from_addr, to_addr.split(","), text)
        server.quit()
