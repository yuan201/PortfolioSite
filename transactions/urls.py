from django.conf.urls import url

from .views import BuyTxnCreateUpdateView, AddTxnView, SellTxnCreateUpdateView, DividendTxnCreateUpdateView, SplitTxnCreateUpdateView
from .views import BuyTxnDeleteView, SellTxnDeleteView, DividendTxnDeleteView, SplitTxnDeleteView
from .views import BuyTxnUpdateView, SellTxnUpdateView, DividendTxnUpdateView, SplitTxnUpdateView


urlpatterns = [
    url(regex=r'^(?P<pk>[0-9]+)/add_buy$',
        view=BuyTxnCreateUpdateView.as_view(),
        name="add_buy"),

    url(regex=r'^(?P<pk>[0-9]+)/add_sell$',
        view=SellTxnCreateUpdateView.as_view(),
        name="add_sell"),

    url(regex=r'^(?P<pk>[0-9]+)/add_divident$',
        view=DividendTxnCreateUpdateView.as_view(),
        name="add_dividend"),

    url(regex=r'^(?P<pk>[0-9]+)/add_split$',
        view=SplitTxnCreateUpdateView.as_view(),
        name="add_split"),

    url(regex=r'^(?P<pk>[0-9]+)/add$',
        view=AddTxnView.as_view(),
        name="add"),

    url(regex=r'^(?P<pk>[0-9]+)/del_buy$',
        view=BuyTxnDeleteView.as_view(),
        name="del_buy"),

    url(regex=r'^(?P<pk>[0-9]+)/del_sell$',
        view=SellTxnDeleteView.as_view(),
        name="del_sell"),

    url(regex=r'^(?P<pk>[0-9]+)/del_dividend$',
        view=DividendTxnDeleteView.as_view(),
        name="del_dividend"),

    url(regex=r'^(?P<pk>[0-9]+)/del_split$',
        view=SplitTxnDeleteView.as_view(),
        name="del_split"),

    url(regex=r'^(?P<pk>[0-9]+)/update_buy$',
        view=BuyTxnUpdateView.as_view(),
        name="update_buy"),

    url(regex=r'^(?P<pk>[0-9]+)/update_sell$',
        view=SellTxnUpdateView.as_view(),
        name="update_sell"),

    url(regex=r'^(?P<pk>[0-9]+)/update_dividend$',
        view=DividendTxnUpdateView.as_view(),
        name="update_dividend"),

    url(regex=r'^(?P<pk>[0-9]+)/update_split$',
        view=SplitTxnUpdateView.as_view(),
        name="update_split"),

]