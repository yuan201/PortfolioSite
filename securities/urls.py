from django.conf.urls import url

from .views import SecCreateView, SecListView, SecUpdateView, SecDelView, SecDetailView


urlpatterns = [
    url(regex=r'^new$',
        view=SecCreateView.as_view(),
        name="new"),

    url(regex=r'^list$',
        view=SecListView.as_view(),
        name="list"),

    url(regex=r'^(?P<pk>[0-9]+)/update$',
        view=SecUpdateView.as_view(),
        name="update"),

    url(regex=r'^(?P<pk>[0-9]+)/del$',
        view=SecDelView.as_view(),
        name="del"),

    url(regex=r'^(?P<pk>[0-9]+)/detail$',
        view=SecDetailView.as_view(),
        name="detail"),

]