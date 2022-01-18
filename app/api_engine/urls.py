from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    FunctionListView,
    FunctionView,
    FunctionCustomerView,
    FunctionExecutionListView,
    FunctionExecutionView,
    EnvironmentVariableView,
    DomainListView,
    DomainView,
    CustomerView,
    CustomerListView,
)

app_name = "api_engine"

urlpatterns = [
    path(
        "function/list/",
        login_required(FunctionListView.as_view()),
        name="function-list",
    ),
    path("function/", login_required(FunctionView.as_view()), name="function"),
    path(
        "function/<int:function_id>",
        login_required(FunctionView.as_view()),
        name="function",
    ),
    path(
        "function/<int:function_id>/customer",
        login_required(FunctionCustomerView.as_view()),
        name="function-customer",
    ),
    path(
        "function/execution/list",
        login_required(FunctionExecutionListView.as_view()),
        name="function-execution-list",
    ),
    path(
        "function/execution/<int:execution_id>",
        login_required(FunctionExecutionView.as_view()),
        name="function-execution",
    ),
    path(
        "environment-variables/<int:function_id>",
        login_required(EnvironmentVariableView.as_view()),
        name="environment-variable",
    ),
    path("domain/list/", login_required(DomainListView.as_view()), name="domain-list"),
    path("domain/", login_required(DomainView.as_view()), name="domain"),
    path("domain/<int:domain_id>", login_required(DomainView.as_view()), name="domain"),
    path(
        "customer/list/",
        login_required(CustomerListView.as_view()),
        name="customer-list",
    ),
    path("customer/", login_required(CustomerView.as_view()), name="customer"),
    path(
        "customer/<int:customer_id>",
        login_required(CustomerView.as_view()),
        name="customer",
    ),
]
