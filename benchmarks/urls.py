from django.conf.urls import url

from .views import BenchmarkCreateView, BenchmarkDetailView, BenchmarkListView
from .views import ConstituteCreateView, ConstituteDeleteView, ConstituteUpdateView, ConstituteNormalizeView

urlpatterns = [
    url(regex=r'^create$',
        view=BenchmarkCreateView.as_view(),
        name="create"),

    url(regex=r'^(?P<pk>[0-9]+)/detail$',
        view=BenchmarkDetailView.as_view(),
        name="detail"),

    url(regex=r'^list$',
        view=BenchmarkListView.as_view(),
        name="list"),

    url(regex=r'^(?P<pk>[0-9]+)/constitute/create$',
        view=ConstituteCreateView.as_view(),
        name="create-cst"),

    url(regex=r'^(?P<pk>[0-9]+)/constitute/delete$',
        view=ConstituteDeleteView.as_view(),
        name="delete-cst"),

    url(regex=r'^(?P<pk>[0-9]+)/constitute/update$',
        view=ConstituteUpdateView.as_view(),
        name="update-cst"),

    url(regex=r'^(?P<pk>[0-9]+)/constitute/normalize$',
        view=ConstituteNormalizeView.as_view(),
        name="normalize-cst"),

]

