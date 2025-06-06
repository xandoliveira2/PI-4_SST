# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this
from apps.authentication.views import firstLoad
from apps.home.views import exibirTodasRuasEncontradas

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    # Auth routes - login / register
    path("", include("apps.authentication.urls")),

    # ADD NEW Routes HERE

    # Leave `Home.Urls` as last the last line
    path("", include("apps.home.urls")),
    # path("exibirTodosDados/",firstLoad),
    # path("exibirTodasRuas/",exibirTodasRuasEncontradas)
]
# 3.2.16
