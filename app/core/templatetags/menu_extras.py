from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    path = ""
    app_names = context["request"].resolver_match.app_names
    if app_names:
        path = app_names[0] + ":"
    path += context["request"].resolver_match.url_name

    for pattern_url in pattern_or_urlname.split(","):
        pattern_url = pattern_url.rstrip().lstrip()
        pattern = pattern_url
        if path == pattern:
            return "active"
    return ""
