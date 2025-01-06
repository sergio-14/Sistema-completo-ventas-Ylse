# myapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Splits the string by the provided delimiter."""
    return value.split(arg)


@register.filter(name='trim')
def trim(value):
    return value.strip() if value else value