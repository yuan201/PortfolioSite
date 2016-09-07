from django.conf.urls import url

from .views import GetQuotesView


urlpatterns = [
    url(regex=r'^(?P<pk>[0-9]+)/get$',
        view=GetQuotesView.as_view(),
        name="get"),
]