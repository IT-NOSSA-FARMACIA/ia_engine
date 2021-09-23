from copy import deepcopy
from typing import Dict, Type

from django.db.models import Model
from django.db.models import Q
from django.contrib.auth.models import User

from .models import (
    CustomerFunctionToken,
    FunctionService,
    FunctionServiceEnvironmentVariable,
    DomainFunctionService,
    Customer,
)
from .utils import generate_token
from core.utils import validate_team_user, get_user_team
from .exceptions import ObjectNotFound
import pydantic


class FunctionServiceBusiness(pydantic.BaseModel):
    """
    Business logic related with schedule
    """

    model_class: Type[Model]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def factory(cls, model_class=FunctionService) -> "FunctionServiceBusiness":
        return cls(model_class=model_class)

    def update_or_create(self, function_id: int, params: Dict, user: User) -> Model:
        # Avoid side effects
        params = deepcopy(params)
        params["last_updated_by"] = user
        if function_id:
            self.model_class.objects.filter(pk=function_id).update(**params)
            object_function = self.model_class.objects.get(pk=function_id)
            object_function.save()  # it is required to enable the historical recording
        else:
            params["created_by"] = user
            object_function = self.model_class.objects.create(**params)
        return object_function

    def get(self, function_id: int = None, user=None) -> Model:
        function_service = self.model_class.objects.get(id=function_id)
        if user and not validate_team_user(user, function_service.team):
            raise ObjectNotFound("Function Not Found")
        return function_service

    def get_query_set(self, params: Dict, user=None):
        name = params.get("name")
        order_by = params.get("order_by", "-id")
        if name:
            object_list = self.model_class.objects.filter(
                Q(name__icontains=name) | Q(description__icontains=name)
            )
        else:
            object_list = self.model_class.objects.all().order_by(order_by)
        if user:
            object_list = object_list.filter(team__in=get_user_team(user))
        return object_list


class FunctionServiceEnvironmentVariableBusiness(pydantic.BaseModel):
    """
    Business logic related with schedule
    """

    model_class: Type[Model]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def factory(
        cls, model_class=FunctionServiceEnvironmentVariable
    ) -> "FunctionServiceEnvironmentVariableBusiness":
        return cls(model_class=model_class)

    def update_or_create(self, function_id, params, pk=0):
        params = deepcopy(params)
        if pk:
            environment_variable = self.model_class.objects.get(id=pk)
            environment_variable.name = params["name"]
            environment_variable.value = params["value"]
            environment_variable.save()
            return environment_variable
        else:
            params["function_service"] = FunctionService.objects.get(pk=function_id)
            print(params)
            # **params
            environment_variable = self.model_class.objects.create(
                name=params["name"],
                value=params["value"],
                function_service=params["function_service"],
            )
            return environment_variable

    def delete(self, environment_id):
        self.model_class.objects.get(pk=environment_id).delete()


class DomainFunctionServiceBusiness(pydantic.BaseModel):
    """
    Business logic related with schedule
    """

    model_class: Type[Model]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def factory(
        cls, model_class=DomainFunctionService
    ) -> "DomainFunctionServiceBusiness":
        return cls(model_class=model_class)

    def update_or_create(self, domain_id, params, user: User):
        params = deepcopy(params)
        params["last_updated_by"] = user
        if domain_id:
            self.model_class.objects.filter(pk=domain_id).update(**params)
            object_domain = self.model_class.objects.get(pk=domain_id)
            object_domain.save()  # it is required to enable the historical recording
        else:
            params["created_by"] = user
            object_domain = self.model_class.objects.create(**params)
        return object_domain

    def get(self, domain_id: int, user=None) -> Model:
        domain = self.model_class.objects.get(id=domain_id)
        if user and not validate_team_user(user, domain.team):
            raise ObjectNotFound("Domain Not Found")
        return domain

    def get_query_set(self, params: Dict, user=None):
        name = params.get("name")
        order_by = params.get("order_by", "-id")
        if name:
            object_list = self.model_class.objects.filter(name__icontains=name)
        else:
            object_list = self.model_class.objects.all().order_by(order_by)
        if user:
            object_list = object_list.filter(team__in=get_user_team(user))
        return object_list


class CustomerBusiness(pydantic.BaseModel):
    """
    Business logic related with schedule
    """

    model_class: Type[Model]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def factory(cls, model_class=Customer) -> "CustomerBusiness":
        return cls(model_class=model_class)

    def update_or_create(self, customer_id, params, user: User):
        params = deepcopy(params)
        params["last_updated_by"] = user
        if customer_id:
            self.model_class.objects.filter(pk=customer_id).update(**params)
            object_customer = self.model_class.objects.get(pk=customer_id)
            object_customer.save()  # it is required to enable the historical recording
        else:
            params["created_by"] = user
            object_customer = self.model_class.objects.create(**params)
        return object_customer

    def get(self, customer_id: int, user: None) -> Model:
        customer = self.model_class.objects.get(id=customer_id)
        if user and not validate_team_user(user, customer.team):
            raise ObjectNotFound("Customer Not Found")
        return customer

    def get_query_set(self, params: Dict, user=None):
        name = params.get("name")
        order_by = params.get("order_by", "-id")
        if name:
            object_list = self.model_class.objects.filter(name__icontains=name)
        else:
            object_list = self.model_class.objects.all().order_by(order_by)
        if user:
            object_list = object_list.filter(team__in=get_user_team(user))
        return object_list


class CustomerFunctionBusiness(pydantic.BaseModel):
    """
    Business logic related with schedule
    """

    model_class: Type[Model]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def factory(cls, model_class=CustomerFunctionToken) -> "CustomerFunctionBusiness":
        return cls(model_class=model_class)

    def update(self, function_id, customer_id, user: User):
        function_customer = self.model_class.objects.get(
            function_service__id=function_id, customer__id=customer_id
        )
        function_customer.last_updated_by = user
        function_customer.token_id = generate_token()
        function_customer.save()
        return function_customer

    def validate_exist(self, function_id, customer_id):
        return self.model_class.objects.filter(
            function_service__id=function_id, customer__id=customer_id
        ).exists()

    def create(self, function_id, customer_id, user: User):
        function_customer = self.model_class.objects.create(
            function_service=FunctionService.objects.get(id=function_id),
            customer=Customer.objects.get(id=customer_id),
            created_by=user,
            last_updated_by=user,
            token_id=generate_token(),
        )
        return function_customer

    def delete(self, function_id, customer_id):
        print("#######")
        print("function_id: ", function_id, "customer_id", customer_id)
        self.model_class.objects.filter(
            function_service__id=function_id, customer__id=customer_id
        ).delete()
