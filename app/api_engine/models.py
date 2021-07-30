from typing import Dict, Tuple, Any
from django.db import models
from core.models import Team
from django.contrib.auth.models import User
from .choices import HTTP_METHOD_CHOICE, HTTP_METHOD_GET
from django.urls import reverse


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

    def __str__(self) -> str:
        return self.name

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

    def __str__(self) -> str:
        return f"{self.domain.url_name}/{self.url_name}"

    @property
    def full_url(self):
        return f"/api/{self.domain.url_name}/{self.url_name}"

    def get_html_hyperlink(self) -> str:
        function_link = reverse("api_engine:function", args=(self.id, ))
        return f"<a href='{function_link}'>{self.name}</a>"

    def execute(self, request) -> Any:
        exec(self.code, globals())            
        return_data = main(request)
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

    def __str__(self) -> str:
        return self.name

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

    def __str__(self) -> str:
        return f"{self.id} - {self.customer.name}"

    class Meta:
        db_table = "customer_function_token"
