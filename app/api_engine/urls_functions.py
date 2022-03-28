from django.urls import path
from .views import (
    execute_function,
    get_openapi_function,
    get_openapi_function_by_domain,
    get_openapi_function_by_team,
)

app_name = "api_engine_functions"

urlpatterns = [
    path(
        "team/<str:team_name>/doc/",
        get_openapi_function_by_team,
        name="execute-function",
    ),
    path(
        "<str:domain_url_name>/doc/",
        get_openapi_function_by_domain,
        name="execute-function",
    ),
    path("<str:domain>/<str:function_url>/", execute_function, name="execute-function"),
    path(
        "<str:domain>/<str:function_url>/doc/",
        get_openapi_function,
        name="execute-function",
    ),
]
