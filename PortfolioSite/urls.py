"""PortfolioSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from portfolios.views import HomePageView


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^portfolios/', include('portfolios.urls', namespace='portfolios')),
    url(r'^txn/', include('transactions.urls', namespace='transactions')),
    url(r'^sec/', include('securities.urls', namespace='securities')),
    url(r'^quotes/', include('quotes.urls', namespace='quotes')),
    url(r'^benchmarks/', include('benchmarks.urls', namespace='benchmarks')),
]
