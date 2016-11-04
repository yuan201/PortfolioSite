from django.conf.urls import url

from .views import TransactionDelView, TransactionUpdateView, TransactionCreateView, TransactionUploadView, TransactionCreateMultipleView


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

    url(regex=r'^(?P<pk>\d+)/upload$',
        view=TransactionUploadView.as_view(),
        name='upload'),

    url(regex=r'^(?P<pk>\d+)/add_n',
        view=TransactionCreateMultipleView.as_view(),
        name='add_n'),
]