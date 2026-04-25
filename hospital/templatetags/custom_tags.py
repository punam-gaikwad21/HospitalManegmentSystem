from django import template

register = template.Library()

@register.filter
def has_attr(obj, name):
    return getattr(obj, name, None) is not None