from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, View
from django.http import (
    JsonResponse,
    HttpRequest,
    HttpResponseNotFound,
    HttpResponse,
)
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required

from .models import (
    DomainFunctionService,
    FunctionService,
    CustomerFunctionToken,
    FunctionServiceEnvironmentVariable,
    Customer,
)
from .business import (
    FunctionServiceBusiness,
    FunctionServiceEnvironmentVariableBusiness,
    DomainFunctionServiceBusiness,
    CustomerBusiness,
    CustomerFunctionBusiness,
)
from .forms import (
    FunctionServiceForm,
    FunctionServiceEnvironmentVariableForm,
    DomainFunctionServiceForm,
    CustomerForm,
)
from django.forms import model_to_dict

from django.conf import settings
from django.contrib import messages


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
        environment_variables = FunctionServiceEnvironmentVariable.objects.filter(
            function_service=function_service
        )
        parameters = {"ENV": {}}
        for environment_variable in environment_variables:
            parameters["ENV"][
                environment_variable.name
            ] = environment_variable.load_value
        response_data = function_service.execute(request, **parameters)
        return JsonResponse(response_data)
    else:
        return JsonResponse({"error": "invalid token"}, status=403)

def get_openapi_function(request, domain, function_url):
    function_service = get_object_or_404(
        FunctionService, url_name=function_url, domain__url_name=domain
    )
    response_data = function_service.get_openapi_schema()
    return HttpResponse(response_data)
    #return JsonResponse(response_data)


@method_decorator(permission_required(settings.API_VIEWER), name="get")
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

    @method_decorator(permission_required(settings.API_DEVELOPER))
    def post(self, request: HttpRequest, function_id: int = 0) -> HttpResponse:
        # actions_id = request.POST.getlist("action")
        form = FunctionServiceForm(request.POST)
        if form.is_valid():
            object_function = self.business.update_or_create(
                function_id=function_id, params=form.cleaned_data, user=request.user
            )
            messages.success(request, settings.FORM_SAVE_MESSAGE_SUCCESS)
            return redirect(reverse("api_engine:function", args=(object_function.id,)))

    @method_decorator(permission_required(settings.API_VIEWER))
    def get(self, request: HttpRequest, function_id: int = None) -> HttpResponse:
        if function_id:
            function = self.business.get(schedule_id=function_id)
            form = FunctionServiceForm(initial=model_to_dict(function))
            environment_variable = FunctionServiceEnvironmentVariable.objects.filter(
                function_service=function
            )
            customer_function = CustomerFunctionToken.objects.filter(
                function_service=function
            )
            customers = Customer.objects.all().order_by("name")
            extra = {"script": function.code}
            extra["function"] = function
            extra["environment_variable"] = environment_variable
            extra["customer_function"] = customer_function
            extra["customers"] = customers
        else:
            extra = {}
            form = FunctionServiceForm()
        return render(
            request,
            "function/function.html",
            {"form": form, "extra": extra},
        )


class EnvironmentVariableView(View):
    business_class = FunctionServiceEnvironmentVariableBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    @method_decorator(permission_required(settings.API_DEVELOPER))
    def post(self, request, function_id):
        form = FunctionServiceEnvironmentVariableForm(request.POST)
        if form.is_valid():
            self.business.update_or_create(
                function_id=function_id,
                params=form.cleaned_data,
                pk=request.POST.get("environment_id", 0),
            )
            messages.success(request, settings.FORM_SAVE_MESSAGE_SUCCESS)
            return redirect(reverse("api_engine:function", args=(function_id,)))

    @method_decorator(permission_required(settings.API_VIEWER))
    def get(self, request, function_id):
        if request.GET.get("method", "").upper() == "DELETE":
            return self.delete(request, function_id)
        return HttpResponseNotFound()

    @method_decorator(permission_required(settings.API_DEVELOPER))
    def delete(self, request, function_id):
        self.business.delete(environment_id=request.GET.get("environment_id"))
        return redirect(reverse("api_engine:function", args=(function_id,)))


class DomainView(View):
    business_class = DomainFunctionServiceBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    @method_decorator(permission_required(settings.API_DEVELOPER))
    def post(self, request: HttpRequest, domain_id: int = 0) -> HttpResponse:
        form = DomainFunctionServiceForm(request.POST)
        if form.is_valid():
            object_domain = self.business.update_or_create(
                domain_id=domain_id, params=form.cleaned_data, user=request.user
            )
            messages.success(request, settings.FORM_SAVE_MESSAGE_SUCCESS)
            return redirect(reverse("api_engine:domain", args=(object_domain.id,)))

    @method_decorator(permission_required(settings.API_VIEWER))
    def get(self, request: HttpRequest, domain_id: int = None) -> HttpResponse:
        extra = {}
        if domain_id:
            domain = self.business.get(domain_id=domain_id)
            form = DomainFunctionServiceForm(initial=model_to_dict(domain))
            extra["domain"] = domain
        else:
            form = DomainFunctionServiceForm()
        return render(
            request,
            "domain/domain.html",
            {"form": form, "extra": extra},
        )


@method_decorator(permission_required(settings.API_VIEWER), name="get")
class DomainListView(ListView):
    template_name = "domain/domain-list.html"
    paginate_by = 10
    model = DomainFunctionService
    business_class = DomainFunctionServiceBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def get_queryset(self):
        return self.business.get_query_set(params=self.request.GET)


class CustomerView(View):
    business_class = CustomerBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    @method_decorator(permission_required(settings.API_DEVELOPER))
    def post(self, request: HttpRequest, customer_id: int = 0) -> HttpResponse:
        form = CustomerForm(request.POST)
        if form.is_valid():
            object_customer = self.business.update_or_create(
                customer_id=customer_id, params=form.cleaned_data, user=request.user
            )
            messages.success(request, settings.FORM_SAVE_MESSAGE_SUCCESS)
            return redirect(reverse("api_engine:customer", args=(object_customer.id,)))

    @method_decorator(permission_required(settings.API_VIEWER))
    def get(self, request: HttpRequest, customer_id: int = None) -> HttpResponse:
        extra = {}
        if customer_id:
            customer = self.business.get(customer_id=customer_id)
            form = CustomerForm(initial=model_to_dict(customer))
            extra["customer"] = customer
        else:
            form = DomainFunctionServiceForm()
        return render(
            request,
            "customer/customer.html",
            {"form": form, "extra": extra},
        )


@method_decorator(permission_required(settings.API_VIEWER), name="get")
class CustomerListView(ListView):
    template_name = "customer/customer-list.html"
    paginate_by = 10
    model = Customer
    business_class = CustomerBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    def get_queryset(self):
        return self.business.get_query_set(params=self.request.GET)


class FunctionCustomerView(View):
    business_class = CustomerFunctionBusiness

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business = self.business_class.factory()

    @method_decorator(permission_required(settings.API_DEVELOPER))
    def post(self, request: HttpRequest, function_id: int = 0) -> HttpResponse:
        customer_id = request.POST.get("customer_id")
        if not self.business.validate_exist(
            function_id=function_id, customer_id=customer_id
        ):
            _ = self.business.create(
                function_id=function_id,
                customer_id=customer_id,
                user=request.user,
            )
            messages.success(request, "Parceiro associado com sucesso")
        else:
            messages.error(request, "Parceiro já se encontra associado")
        return redirect(reverse("api_engine:function", args=(function_id,)))

    @method_decorator(permission_required(settings.API_VIEWER))
    def get(self, request, function_id):
        if request.GET.get("method", "").upper() == "DELETE":
            return self.delete(request, function_id)
        if request.GET.get("method", "").upper() == "PUT":
            return self.put(request, function_id)
        return HttpResponseNotFound()

    @method_decorator(permission_required(settings.API_DEVELOPER))
    def put(self, request, function_id):
        _ = self.business.update(
            function_id=function_id,
            customer_id=request.GET.get("customer_id"),
            user=request.user,
        )
        messages.success(request, "Token regerado com sucesso")
        return redirect(reverse("api_engine:function", args=(function_id,)))

    @method_decorator(permission_required(settings.API_DEVELOPER))
    def delete(self, request, function_id):
        self.business.delete(
            function_id=function_id, customer_id=request.GET.get("customer_id")
        )
        return redirect(reverse("api_engine:function", args=(function_id,)))
