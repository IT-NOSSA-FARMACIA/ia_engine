from django.contrib import admin

from django.contrib import admin
from .models import (
    FunctionService,
    DomainFunctionService,
    CustomerFunctionToken,
    Customer,
    FunctionServiceEnvironmentVariable,
)


admin.site.register(FunctionService)
admin.site.register(DomainFunctionService)
admin.site.register(CustomerFunctionToken)
admin.site.register(Customer)
admin.site.register(FunctionServiceEnvironmentVariable)
