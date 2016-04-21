"""HG URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
import settings
from website.views import *
from website.users import *

urlpatterns = [
    url(r'^html$', testhtml),
    url(r'^test$', test),
    url(r'^testcycle$', addcycle),
    url(r'^$', index),
    url(r'^login$', login),
    url(r'^logout$', logout),
    url(r'^newcontract$', newcontract),
    url(r'^statuscontract$', statuscontract),
    url(r'^querycontracts$', querycontracts),
    url(r'^newfield$', newfield),
    url(r'^newparty$', newparty),
    url(r'^newmanager$', newmanager),
    url(r'^newproduct$', newproduct),
    url(r'^settings$', userctl),
    url(r'^adduser$', adduser),
    url(r'^deleteuser$', deleteuser),
]
