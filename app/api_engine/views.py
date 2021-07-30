from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, View
from django.http import (
    JsonResponse,
    HttpRequest,
    HttpResponseNotFound,
    HttpResponse,
    HttpResponseForbidden,
)
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

from .models import FunctionService, CustomerFunctionToken
from .business import FunctionServiceBusiness
from .forms import FunctionServiceForm
from django.forms import model_to_dict


@csrf_exempt
def execute_function(request, domain, function_url):
    function_service = get_object_or_404(
        FunctionService, url_name=function_url, domain__url_name=domain
    )
    if function_service.http_method not in request.method:
        return HttpResponseNotFound()

    token_function = CustomerFunctionToken.objects.filter(
        token_id=request.headers.get("Api-Key"), function_service=function_service
    ).exists()
    if token_function:
        response_data = function_service.execute(request)
        return JsonResponse(response_data)
    else:
        return JsonResponse({"error": "invalid token"}, status=403)

class FunctionListView(ListView):
    template_name = "function/function-list.html"
    paginate_by = 10
    model = FunctionService
    business_class = FunctionServiceBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def get_queryset(self):
        return self.business.get_query_set(params=self.request.GET)

class FunctionView(View):
    business_class = FunctionServiceBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def post(self, request: HttpRequest, function_id: int = 0) -> HttpResponse:
        #actions_id = request.POST.getlist("action")
        form = FunctionServiceForm(request.POST)
        if form.is_valid():
            object_function = self.business.update_or_create(
                function_id=function_id, params=form.cleaned_data
            )
            return redirect(reverse("api_engine:function", args=(object_function.id, )))

    

    def get(self, request: HttpRequest, function_id: int = None) -> HttpResponse:
        if function_id:
            function = self.business.get(schedule_id=function_id)
            form = FunctionServiceForm(initial=model_to_dict(function))
            #step_schedule = StepSchedule.objects.filter(schedule=schedule)
            #environment_variable = ScheduleEnvironmentVariable.objects.filter(
            #    schedule=schedule
            #)
            extra = {"script": function.code}
            extra["function"] = function
            #extra["environment_variable"] = environment_variable
            formset = {}
        else:
            schedule = None
            extra = {}
            form = FunctionServiceForm()
            #formset = StepFormSet()
        #extra["actions"] = Action.objects.filter()
        return render(
            request,
            "function/function.html", 
            {"form": form, "extra": extra},
        )

    # def get_form_kwargs(self):
    #     """Passes the request object to the form class.
    #     This is necessary to only display members that belong to a given user"""

    #     kwargs = super(ScheduleView, self).get_form_kwargs()
    #     kwargs["request"] = self.request
    #     return kwargs