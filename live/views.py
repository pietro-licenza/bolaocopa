"""
HTTP views for the ``live`` app.

Exposes two endpoints:

* :class:`MatchSyncView` — wired to the "Buscar resultado" button
  rendered next to each match. Triggers an upstream sync, enforcing
  daily and per-minute rate limits, and redirects back to the page
  that issued the request with a status message.
* :class:`MatchCardPartialView` — returns the HTML of a single match
  card (the same partial used by the match list pages) so the
  frontend can poll it every 60 seconds for games in progress (see
  US-7.4 "Indicador Ao vivo e placar em tempo real").

Both views are intentionally thin: rate-limit checks and message
rendering live here, while the actual API call + field mapping is
delegated to ``live.services.sync.sync_match_from_api`` so the same
logic can be reused from a future cron / management command.
"""

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from matches.models import Match
from predictions.models import Prediction

from live.services import rate_limit
from live.services.sync import sync_match_from_api


logger = logging.getLogger(__name__)


class MatchCardPartialView(LoginRequiredMixin, TemplateView):
    """Return the rendered HTML of a single match card.

    Used by the polling script in
    ``templates/live/partials/poll_script.html``: every 60 seconds, the
    browser fetches ``/matches/<id>/_partial/`` for each card whose
    ``data-live="1"`` (i.e. match in progress) and swaps the article's
    inner HTML for the freshly rendered version. This is the only
    legitimate exception to the "DTL puro, zero JS" rule, called out
    in US-7.4 because live scores cannot be served server-pushed from
    this stack.

    The view uses :class:`TemplateView` (not :class:`TemplateResponse`)
    directly to keep the contract minimal: it always renders the same
    template with the looked-up match in context and returns the
    resulting HTML body. A 404 is raised automatically when the match
    does not exist, so polling a stale id is a clean failure rather
    than a silent no-op.

    The ``user_has_predicted`` flag is computed from the requesting
    user so the polling response stays consistent with the initial
    render of the same card (e.g. on ``match_list.html``).
    """

    template_name = 'live/partials/match_card.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        match = get_object_or_404(Match, pk=kwargs['match_id'])
        context['match'] = match
        # Reuse the same "user has a prediction for this match"
        # lookup as the match list views so the partial stays
        # visually consistent across the initial page load and the
        # subsequent polls.
        context['user_has_predicted'] = Prediction.objects.filter(
            user=self.request.user,
            match=match,
        ).exists()
        return context


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
