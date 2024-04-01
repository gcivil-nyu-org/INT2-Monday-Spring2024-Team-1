from django import template

register = template.Library()


@register.filter
def first_300_characters(value):
    if len(value) <= 300:
        return value
    else:
        return value[:300] + "..."
