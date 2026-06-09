"""
Custom URL path converters for the ``matches`` app.

A converter is a small class with a ``regex`` attribute plus
``to_python`` / ``to_url`` methods. Django matches the URL segment
against ``regex``; on a hit, ``to_python`` converts the raw string
to a Python object and ``to_url`` does the reverse (used by
``reverse()`` and the ``{% url %}`` template tag).

See: https://docs.djangoproject.com/en/6.0/topics/http/urls/#registering-custom-path-converters
"""

import datetime


class DateConverter:
    """Match ISO ``YYYY-MM-DD`` date strings in URL paths.

    ``to_python`` parses the segment into a ``datetime.date``. The
    ``ValueError`` raised by :func:`datetime.date.fromisoformat` on an
    invalid date is intentionally allowed to bubble up — Django turns
    it into a 404, which is the correct HTTP response for a malformed
    date in the URL.

    ``to_url`` accepts either a ``datetime.date`` (or ``datetime``)
    object — anything that exposes an ``isoformat()`` method — or a
    string. Strings are passed through unchanged so that views can
    do ``reverse('match_schedule', kwargs={'date': '2026-06-15'})``
    without having to first build a ``date`` instance.
    """

    regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}'

    def to_python(self, value):
        return datetime.date.fromisoformat(value)

    def to_url(self, value):
        if hasattr(value, 'isoformat'):
            return value.isoformat()
        return str(value)
