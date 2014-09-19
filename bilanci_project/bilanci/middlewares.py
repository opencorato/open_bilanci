import re
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect
from bilanci.views import HomeTemporaryView, PageNotFoundTemplateView, BilancioDettaglioView, BilancioOverServicesView
from services.models import PaginaComune


class PrivateBetaMiddleware(object):
    """
    Add this to your ``MIDDLEWARE_CLASSES`` make all views except for
    those in the account application require that a user be logged in.
    This can be a quick and easy way to restrict views on your site,
    particularly if you remove the ability to create accounts.
    **Settings:**
    ``EARLYBIRD_ENABLE``
    Whether or not the beta middleware should be used. If set to `False`
    the PrivateBetaMiddleware middleware will be ignored and the request
    will be returned. This is useful if you want to disable early bird
    on a development machine. Default is `True`.
    """

    def __init__(self):
        self.enable_beta = settings.EARLYBIRD_ENABLE

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated() or not self.enable_beta:
            # User is logged in, no need to check anything else.
            return

        whitelisted_modules = ['django.contrib.auth.views', 'django.views.static', 'django.contrib.admin.sites']
        if '%s' % view_func.__module__ in whitelisted_modules:
            return
        else:
            return HomeTemporaryView.as_view()(request)



class ComuniServicesMiddleware(object):

    def process_request(self, request):
        True == True
        return


    def process_view(self, request, view_func, view_args, view_kwargs):

        """
        ComuniServicesMiddleware serves to enable the Servizi ai Comuni.
        The request is filtered by the http_host: if the host belongs to a Comune
        that has activated the services then the special template is shown for
        Dettaglio, Composizione e Indicatori views.

        If the request comes from the production / staging host then no action is taken.

        In all other cases a 404 page is shown
        """

        # http_host gets the http_host string removing the eventual port number
        regex = re.compile("(.*)(?::)")
        http_host = regex.findall(request.META['HTTP_HOST'])[0]

        if http_host in settings.HOSTS_COMUNI:

            try:
                pagina_comune = PaginaComune.objects.get(
                    host = http_host,
                    active = True
                )
            except ObjectDoesNotExist:
                return PageNotFoundTemplateView.as_view()(request)

            else:

                whitelisted_views = {
                    'BilancioView':None,
                    'BilancioNotFoundView': None,
                    'BilancioOverView': BilancioOverServicesView,
                    'BilancioDettaglioView': None,
                    'BilancioIndicatoriView': None,
                    'BilancioComposizioneView': None,
                    'BilancioCompositionWidgetView': None,
                    'BilancioRedirectView': None
                }

                if view_func.func_name not in whitelisted_views.keys():
                    return PageNotFoundTemplateView.as_view()(request)
                else:
                    return whitelisted_views[view_func.func_name].as_view()(request)



        return
