# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view, register_user ,firstLoad
from django.contrib.auth.views import LogoutView
from apps.home.views import exibirTodasRuasEncontradas

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("exibirTodosDados/",firstLoad),
    path("exibirTodasRuas/",exibirTodasRuasEncontradas)
    
]
