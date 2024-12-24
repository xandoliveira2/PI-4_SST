# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    senha = models.CharField(max_length=20)
    email = models.CharField(max_length=200)

