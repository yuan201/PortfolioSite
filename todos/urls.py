from django.conf.urls import url

from .views import TodoCreateView, TodoUpdateView


urlpatterns = [
    url(regex=r'^create$',
        view=TodoCreateView.as_view(),
        name='create'),

    url(regex=r'^(?P<pk>[0-9]+)/detail$',
        view=TodoUpdateView.as_view(),
        name='update'),

]