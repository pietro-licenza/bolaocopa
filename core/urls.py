from django.contrib import admin
from django.urls import path, include, register_converter

from matches.converters import DateConverter


# Register the ISO ``YYYY-MM-DD`` date converter used by the
# matches schedule URL (``/matches/schedule/<date:date>/``). See
# US-7.7. The converter is also reusable by any future view that
# needs a date path segment.
register_converter(DateConverter, 'date')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('pools.urls')),
    path('', include('predictions.urls')),
    path('', include('rankings.urls')),
    path('', include('live.urls')),
    # US-7.7: mount the "Jogos" app under /matches/. Inside
    # ``matches/urls.py`` the empty path resolves to the landing
    # page (``MatchHomeView``), and the rest of the routes add the
    # schedule / groups / bracket segments.
    path('matches/', include('matches.urls')),
]
