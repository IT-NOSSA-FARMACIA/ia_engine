from django import template

register = template.Library()

BADGE_STATUS = {
    "PE": "bg-light",
    "PR": "bg-primary",
    "SC": "bg-success",
    "ER": "bg-danger",
    "QU": "bg-warning",
}


@register.simple_tag()
def badge_status_execution(status):
    return BADGE_STATUS.get(status, "bg-light")
