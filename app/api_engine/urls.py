
from django.urls import path
from .views import FunctionListView, FunctionView

app_name = "api_engine"

urlpatterns = [
    path("function/list/", FunctionListView.as_view(), name="function-list"),
    path("function/", FunctionView.as_view(), name="function"),
    path("function/<int:function_id>", FunctionView.as_view(), name="function"),
]