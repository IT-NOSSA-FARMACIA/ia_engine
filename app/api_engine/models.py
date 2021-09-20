from typing import Any
from simple_history.models import HistoricalRecords

from django.db import models
from django.core import signing
from django.contrib.auth.models import User
from django.urls import reverse

from core.models import Team
from .choices import HTTP_METHOD_CHOICE, HTTP_METHOD_GET


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
    history = HistoricalRecords()

    def __str__(self) -> str:
        return f"{self.domain.url_name}/{self.url_name}"

    @property
    def full_url(self):
        return f"/api/{self.domain.url_name}/{self.url_name}"

    def get_html_hyperlink(self) -> str:
        function_link = reverse("api_engine:function", args=(self.id,))
        return f"<a href='{function_link}'>{self.name}</a>"

    def get_openapi_schema(self):
        from openapi_schema_pydantic import OpenAPI
        from openapi_schema_pydantic.util import (
            PydanticSchema,
            construct_open_api_with_schema_class,
        )

        exec(self.code, globals())
        content_request = {}
        content_response = {}
        try:
            content_request["application/json"] = {
                "schema": PydanticSchema(schema_class=Request)
            }
        except NameError:
            pass

        try:
            content_response["application/json"] = {
                "schema": PydanticSchema(schema_class=Response)
            }
        except NameError:
            pass

        open_api_obj = OpenAPI.parse_obj(
            {
                "info": {
                    "title": f"{self.name}",
                    "version": "v1",
                    "description": f"{self.description}",
                },
                "paths": {
                    f"{self.full_url}": {
                        f"{self.get_http_method_display().lower()}": {
                            "requestBody": {"content": content_request},
                            "responses": {
                                "200": {
                                    "description": "",
                                    "content": content_response,
                                }
                            },
                        }
                    },
                },
                "components": {
                    "securitySchemes": {
                        "Api-Key": {
                            "type": "http",
                            "scheme": "bearer",
                            "bearerFormat": "JWT",
                        }
                    }
                },
            }
        )
        open_api = construct_open_api_with_schema_class(open_api_obj)
        open_api.openapi = "3.0.0"
        openapi_json = open_api.json(by_alias=True, exclude_none=True, indent=4)
        return openapi_json

    def execute(self, request, *args, **kwargs) -> Any:
        exec(self.code, globals())
        try:
            return_data = main(request, *args, **kwargs)
        except Exception as ex:
            return {"error": str(ex)}
        return return_data

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
