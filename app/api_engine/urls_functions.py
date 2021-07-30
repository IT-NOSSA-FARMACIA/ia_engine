from django.urls import path, re_path
from .views import execute_function

app_name = "api_engine_functions"

urlpatterns = [
    path("<str:domain>/<str:function_url>/", execute_function, name="execute-function")
]