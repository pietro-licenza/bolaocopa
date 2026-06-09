"""
HTTP views for the ``live`` app.

Currently exposes a single endpoint — :class:`MatchSyncView` — wired
to the "Buscar resultado" button rendered next to each match. The
view is intentionally thin: rate-limit checks and message rendering
live here, while the actual API call + field mapping is delegated to
``live.services.sync.sync_match_from_api`` so the same logic can be
reused from a future cron / management command.
"""

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from matches.models import Match

from live.services import rate_limit
from live.services.sync import sync_match_from_api


logger = logging.getLogger(__name__)


class MatchSyncView(LoginRequiredMixin, View):
    """Manually trigger a single-match sync from the upstream APIs.

    * POST only — GET returns 405 to keep the endpoint non-idempotent
      and avoid accidental triggers from prefetchers / link previews.
    * Requires authentication (``LoginRequiredMixin``).
    * Requires the match to have a non-null ``external_id`` — without
      it there is nothing to look up, so we redirect with an error.
    * Enforces a daily rate-limit *before* the API call, and a
      per-minute FDO limit. When the daily cap is hit, the view
      short-circuits without hitting the network.
    """

    http_method_names = ['post', 'options']

    def post(self, request, match_id):
        match = get_object_or_404(Match, pk=match_id)

        if match.external_id is None:
            messages.error(
                request,
                'Este jogo ainda não possui identificador externo; '
                'sincronização indisponível.',
            )
            return self._redirect_back(request)

        if rate_limit.is_daily_limit_reached():
            logger.info(
                '[Sync] Daily rate limit reached; refusing match %s sync.',
                match.pk,
            )
            messages.error(
                request,
                'Limite diario da API atingido, tente amanha.',
            )
            return self._redirect_back(request)

        if rate_limit.check_fdo_minute_limit():
            logger.info(
                '[Sync] FDO per-minute limit reached; refusing match %s sync.',
                match.pk,
            )
            messages.error(
                request,
                'Limite de requisicoes por minuto atingido. '
                'Aguarde alguns segundos e tente novamente.',
            )
            return self._redirect_back(request)

        result = sync_match_from_api(match)

        if not result.success:
            messages.error(
                request,
                result.error
                or 'Nao foi possivel atualizar o jogo. Tente novamente.',
            )
            return self._redirect_back(request)

        messages.success(request, 'Placar atualizado')
        return self._redirect_back(request)

    def _redirect_back(self, request):
        """Send the user back to the page that issued the request.

        Falls back to the global matches list when no ``Referer`` is
        present (e.g. the form was submitted from a script).
        """
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect(reverse('match_list'))
