# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
# from django.contrib.auth.models import User

# Create your models here.

class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    senha = models.CharField(max_length=20)
    email = models.CharField(max_length=200)
    
    def __init__(self, nome , senha , email):
        self.nome = nome
        self.senha = senha
        self.email = email
     
    class Meta:
        db_table = "usuarios"
    
    
class Endereco(models.Model):
    rua = models.CharField(max_length=255)
    bairro = models.CharField(max_length=255)
    cep = models.CharField(max_length=255, primary_key=True, db_index=True)

    def __str__(self):
        return f"r> {self.rua} / bairro> {self.bairro} / cep> {self.cep}"
    class Meta:
        db_table = "enderecos"
