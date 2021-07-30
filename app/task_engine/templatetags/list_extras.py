import re

from django import template

from django.urls import reverse, NoReverseMatch


register = template.Library()


@register.simple_tag()
def order_by(key, order_by):
    if order_by and order_by[0] == "-" and key == order_by[1:]:
        return '<i data-feather="arrow-up" width="20"></i>'
    elif key == order_by:
        return '<i data-feather="arrow-down" width="20"></i>'
    else:
        return '<i data-feather="arrow-up" width="20"></i><i data-feather="arrow-down" width="20"></i>'

@register.simple_tag()
def order_by_href(key, order_by, search_name=None):
    params = ""
    if search_name:
        params = f"&name={search_name}"
    if order_by and order_by[0] == "-":
        return f"?{params}"
    elif key == order_by:
        return f"?order_by=-{order_by}{params}"
    else:
        return f"?order_by={key}{params}"

@register.simple_tag()
def get_params_list(params):
    order_by_field = params.get("order_by")
    params_list = ""
    if order_by_field:
        params_list = f"order_by={order_by_field}"
    name_search_field = params.get("name")
    if name_search_field:
        params_list += f"&name={name_search_field}"
    return params_list