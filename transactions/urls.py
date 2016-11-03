from django.conf.urls import url

from .views import TransactionDelView, TransactionUpdateView, TransactionCreateView


urlpatterns = [
    url(regex=r'^(?P<pk>\d+)/update$',
        view=TransactionUpdateView.as_view(),
        name="update"),

    url(regex=r'^(?P<pk>\d+)/del$',
        view=TransactionDelView.as_view(),
        name='del'),

    url(regex=r'^(?P<pk>\d+)/add$',
        view=TransactionCreateView.as_view(),
        name='add'),

]