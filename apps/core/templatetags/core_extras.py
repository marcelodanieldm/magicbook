"""Custom template filters used by MagicBook frontend templates."""

from django import template

register = template.Library()


@register.filter(name='dict_get')
def dict_get(d, key):
    """Return d[key] from a dict, safely."""
    try:
        return d[key]
    except (KeyError, TypeError):
        return ''
