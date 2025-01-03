from django import template

register = template.Library()

@register.filter
def times(value):
    try:
        return range(int(value))
    except ValueError:
        return []
