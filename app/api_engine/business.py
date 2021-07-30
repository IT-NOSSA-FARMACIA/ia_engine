from copy import deepcopy
from typing import Dict, Type, List

from django.db.models import Model
from django.db.models import Q

from .models import (
    FunctionService
)

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

    def update_or_create(self, function_id: int, params: Dict) -> Model:
        # Avoid side effects
        params = deepcopy(params)
        print(params)
        # script_code = params["script"]
        # del params["script"]
        # del params["action"]
        print(function_id)
        print(bool(function_id))
        if function_id:
            self.model_class.objects.filter(pk=function_id).update(**params)
            object_function = self.model_class.objects.get(pk=function_id)
            #Script.objects.filter(pk=object_schedule.script.pk).update(code=script_code)
        else:
            #script = Script.objects.create(code=script_code)
            #params["script"] = script
            object_function = self.model_class.objects.create(**params)
        return object_function

    def get(self, schedule_id: int = None) -> Model:
        return self.model_class.objects.get(id=schedule_id)

    def get_query_set(self, params: Dict):
        name = params.get("name")
        order_by = params.get("order_by", "-id")
        if name:
            object_list = self.model_class.objects.filter(
                Q(name__icontains=name) | Q(description__icontains=name)
            )
        else:
            object_list = self.model_class.objects.all().order_by(order_by)
        return object_list