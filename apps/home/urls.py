# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from apps.home.views import exibirTodasRuasEncontradas

urlpatterns = [

    path("exibirTodasRuas/",exibirTodasRuasEncontradas),
    # The home page
    path('', views.index, name='home'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
