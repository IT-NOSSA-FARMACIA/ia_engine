from django.urls import path
from .views import execute_function, get_openapi_function

app_name = "api_engine_functions"

urlpatterns = [
    path("<str:domain>/<str:function_url>/", execute_function, name="execute-function"),
    path("<str:domain>/<str:function_url>/doc/", get_openapi_function, name="execute-function")
]