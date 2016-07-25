from django.conf.urls import url

from .views import BuyTxCreateView, AddTxnView, SellTxCreateView, DividendTxCreateView, SplitTxCreateView


urlpatterns = [
    url(regex=r'^(?P<pk>[0-9]+)/add_buy$',
        view=BuyTxCreateView.as_view(),
        name="add_buy"),

    url(regex=r'^(?P<pk>[0-9]+)/add_sell$',
        view=SellTxCreateView.as_view(),
        name="add_sell"),

    url(regex=r'^(?P<pk>[0-9]+)/add_divident$',
        view=DividendTxCreateView.as_view(),
        name="add_dividend"),

    url(regex=r'^(?P<pk>[0-9]+)/add_split$',
        view=SplitTxCreateView.as_view(),
        name="add_split"),

    url(regex=r'^(?P<pk>[0-9]+)/add$',
        view=AddTxnView.as_view(),
        name="add"),


]