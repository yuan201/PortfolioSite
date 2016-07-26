from django.conf.urls import url

from .views import BuyTxnCreateView, AddTxnView, SellTxnCreateView, DividendTxnCreateView, SplitTxnCreateView
from .views import BuyTxnDeleteView, SellTxnDeleteView, DividendTxnDeleteView, SplitTxnDeleteView


urlpatterns = [
    url(regex=r'^(?P<pk>[0-9]+)/add_buy$',
        view=BuyTxnCreateView.as_view(),
        name="add_buy"),

    url(regex=r'^(?P<pk>[0-9]+)/add_sell$',
        view=SellTxnCreateView.as_view(),
        name="add_sell"),

    url(regex=r'^(?P<pk>[0-9]+)/add_divident$',
        view=DividendTxnCreateView.as_view(),
        name="add_dividend"),

    url(regex=r'^(?P<pk>[0-9]+)/add_split$',
        view=SplitTxnCreateView.as_view(),
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

]