"""
Custom template tags / filters for the ``matches`` app.

Currently exposes a single ``get_item`` filter that lets templates
look up a key on a dict (or attribute on an object). Django's built-in
template language does not support ``dict|key`` lookups by variable
key, so this is the standard workaround.
"""

from django import template


register = template.Library()


@register.filter(name='get_item')
def get_item(value, key):
    """Return ``value[key]`` if ``value`` supports item access.

    Returns ``None`` for missing keys (which Django then treats as
    the template's "undefined" sentinel) so the template can use
    the ``{% if x|get_item:k %}`` idiom naturally.
    """
    if value is None:
        return None
    try:
        return value[key]
    except (KeyError, IndexError, TypeError):
        try:
            return getattr(value, str(key))
        except AttributeError:
            return None
