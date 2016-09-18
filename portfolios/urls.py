from django.conf.urls import url

from .views import PortfolioCreateView, PortfolioDetailView, PortfolioListView

urlpatterns = [
    url(regex=r'^new$',
        view=PortfolioCreateView.as_view(),
        name="new"),

    url(regex=r'^(?P<pk>[0-9]+)/detail$',
        view=PortfolioDetailView.as_view(),
        name="detail"),

    url(regex=r'^list$',
        view=PortfolioListView.as_view(),
        name="list"),
]
