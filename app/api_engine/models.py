from core.models import Team
from contextlib import redirect_stdout

from django.db import models
from django.core import signing
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings

from functools import cached_property

from io import StringIO
from simple_history.models import HistoricalRecords
from typing import Any

from .choices import HTTP_METHOD_CHOICE, HTTP_METHOD_GET
from .constants import FUNCTION_REQUEST_CLASS_NAME, FUNCTION_RESPONSE_CLASS_NAME

import json
import traceback
import sys


class DomainFunctionService(models.Model):
    name = models.CharField(max_length=500)
    url_name = models.CharField(max_length=500)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="domain_function_service_created_by",
    )
    last_updated_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="domain_function_service_last_updated_by",
    )
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name

    def get_html_hyperlink(self) -> str:
        domain_link = reverse("api_engine:domain", args=(self.id,))
        return f"<a href='{domain_link}'>{self.name}</a>"

    class Meta:
        db_table = "domain_function_service"


class FunctionService(models.Model):
    name = models.CharField(max_length=500)
    domain = models.ForeignKey(DomainFunctionService, on_delete=models.CASCADE)
    url_name = models.CharField(max_length=500)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="function_server_created_by",
    )
    last_updated_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="function_server_last_updated_by",
    )
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    http_method = models.CharField(
        max_length=3, choices=HTTP_METHOD_CHOICE, default=HTTP_METHOD_GET
    )
    code = models.TextField()
    active = models.BooleanField(default=True)
    public = models.BooleanField(default=False)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return f"{self.domain.url_name}/{self.url_name}"

    @property
    def full_url(self):
        return f"/api/{self.domain.url_name}/{self.url_name}/"

    def get_html_hyperlink(self) -> str:
        function_link = reverse("api_engine:function", args=(self.id,))
        return f"<a href='{function_link}'>{self.name}</a>"

    @property
    def swagger_doc_url(self):
        return f"{settings.SWAGGER_URL_TO_DOC}?url={self.full_url}" + "doc/"

    @cached_property
    def has_request_class(self):
        return FUNCTION_REQUEST_CLASS_NAME in self.code

    @cached_property
    def has_response_class(self):
        return FUNCTION_REQUEST_CLASS_NAME in self.code

    def execute(self, request, customer=None, *args, **kwargs) -> Any:
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout):
            exec(self.code, globals())
            try:
                response_data = main(request, *args, **kwargs)
                if isinstance(response_data, tuple):
                    return_data, status_code = response_data
                else:
                    return_data = return_data
                    status_code = 200
            except Exception as ex:
                status_code = 400
                return_data = {"error": str(ex)}
                with redirect_stdout(stderr):
                    traceback.print_exc(file=sys.stdout)

        script_log = stdout.getvalue() + stderr.getvalue()
        FunctionServiceExecution.objects.create(
            function_service=self,
            output=script_log,
            response=return_data,
            request=request.body or request.GET or request.POST,
            customer=customer,
            status_code=status_code,
        )
        return status_code, return_data

    class Meta:
        db_table = "function_service"


class Customer(models.Model):
    name = models.CharField(max_length=500)
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="customer_created_by",
    )
    last_updated_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="customer_last_updated_by",
    )
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name

    def get_html_hyperlink(self) -> str:
        customer_link = reverse("api_engine:customer", args=(self.id,))
        return f"<a href='{customer_link}'>{self.name}</a>"

    class Meta:
        db_table = "customer"


class CustomerFunctionToken(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    token_id = models.CharField(max_length=100)
    function_service = models.ForeignKey(FunctionService, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="customer_function_token_created_by",
    )
    last_updated_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="customer_function_token_last_updated_by",
    )
    history = HistoricalRecords()

    def __str__(self) -> str:
        return f"{self.id} - {self.customer.name}"

    class Meta:
        db_table = "customer_function_token"


class FunctionServiceEnvironmentVariable(models.Model):
    function_service = models.ForeignKey(FunctionService, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=500)
    history = HistoricalRecords()

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        old_schedule_env = FunctionServiceEnvironmentVariable.objects.filter(
            id=self.id
        ).first()
        old_value = old_schedule_env.value if old_schedule_env else ""
        if self.value != old_value:
            self.value = signing.dumps(self.value)
        return super().save(*args, **kwargs)

    @property
    def load_value(self) -> str:
        return signing.loads(self.value)

    class Meta:
        db_table = "function_service_environment_variable"


class FunctionServiceExecution(models.Model):
    function_service = models.ForeignKey(FunctionService, on_delete=models.CASCADE)
    created_dt = models.DateTimeField(auto_now_add=True)
    output = models.TextField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    request = models.TextField(blank=True, null=True)
    customer = models.ForeignKey(
        Customer, blank=True, null=True, on_delete=models.DO_NOTHING
    )
    status_code = models.IntegerField(blank=True, null=True)

    def get_html_hyperlink(self) -> str:
        function_link = reverse("api_engine:function-execution", args=(self.id,))
        return f"<a href='{function_link}'>{self.id}</a>"

    def get_badge_status_code(self) -> str:
        badge_status = "info"
        if self.status_code:
            if self.status_code >= 200 and self.status_code < 300:
                badge_status = "success"
            elif self.status_code >= 300 and self.status_code < 400:
                badge_status = "warning"
            elif self.status_code >= 400 and self.status_code < 600:
                badge_status = "danger"
        badge = f"<span class='badge bg-{badge_status}'>{self.status_code}</span>"
        return badge

    def __str__(self) -> str:
        return self.function_service.name

    class Meta:
        db_table = "function_service_execution"
