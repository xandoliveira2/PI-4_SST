# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from pymongo import MongoClient
from json import load
from django.http import JsonResponse


def login_view(request):
    print("Login view aqui entra no print")
    print("Login view aqui entra no print")
    print("Login view aqui entra no print")
    print("Login view aqui entra no print")
    print("Login view aqui entra no print")
    print("Login view aqui entra no print")
    print("Login view aqui entra no print")
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})
import pandas as pd
def firstLoad(request):
    print('CHEGOU AQUI')
    print('CHEGOU AQUI')
    print('CHEGOU AQUI')
    print('CHEGOU AQUI')
    print('CHEGOU AQUI')
    client = MongoClient('mongodb://localhost:27017/')
    db = client['teste']
    colecao = db['teste2']
    resultado = colecao.find().sort([
    ("data", -1),  # Ordena por data (decrescente)
    ("hora", -1)   # Depois ordena por hora (decrescente)
    ])
    df = pd.DataFrame(colecao.find())
    dados = list(resultado)        
    for doc in dados:
        doc['_id'] = str(doc['_id'])  # Para evitar erro ao retornar JSON
        filtro_data = request.GET.get('param1')
    filtro_hora = request.GET.get('param2')
    filtro_veiculos = request.GET.get('param3', 'carros motos')#('param3', 'carros motos')  # Default para 'carros motos'
    ruas = request.GET.get('ruas')
    ruas = ruas.split(',') if ruas else []
    

    filtro_veiculos = filtro_veiculos.split()
    while '' in filtro_veiculos:
        filtro_veiculos.remove('')
    
    base = ['rua','total'] + filtro_veiculos
    from datetime import datetime
    if filtro_hora and filtro_data:
        if len(filtro_data.split('-')) == 2 :
            data_inicio_str, data_fim_str = filtro_data.split('-')

            # Converte strings para objetos de hora
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y").date()

            # Garante que df['hora'] está no formato de hora
            df['data'] = pd.to_datetime(df['data'], format="%d/%m/%Y").dt.date

            # Agora filtra com base no intervalo de horas
            if filtro_data.split('-')[0] == '': 
                df = df[(df['data'] <= data_fim)]
            elif filtro_data.split('-')[1] == '':
                df = df[(df['data'] >= data_inicio)]
            else:
                df = df[(df['data'] >= data_inicio) & (df['data'] <= data_fim)]
                
        if len(filtro_hora.split('-')) == 2 :
            hora_inicio_str, hora_fim_str = filtro_hora.split('-')

            # Converte strings para objetos de hora
            hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()
            hora_fim = datetime.strptime(hora_fim_str, "%H:%M").time()

            # Garante que df['hora'] está no formato de hora
            df['hora'] = pd.to_datetime(df['hora'], format="%H:%M").dt.time

            # Agora filtra com base no intervalo de horas
            if filtro_hora.split('-')[0] == '': 
                df_filtered1 = df[(df['hora'] <= hora_fim)]
            elif filtro_hora.split('-')[1] == '':
                df_filtered1 = df[(df['hora'] >= hora_inicio)]
            else:
                df_filtered1 = df[(df['hora'] >= hora_inicio) & (df['hora'] <= hora_fim)]
        
        print("Com filtro:")
        print(df_filtered1)
        df_filtered1 = df_filtered1.applymap(str)  # Converte todos os valores para string
        data = df_filtered1.to_dict(orient='records')
    else:
        print("Sem filtro:")
        print(df)
        df = df.applymap(str)
        data = df.to_dict(orient='records')

    return JsonResponse(data, safe=False)
    
def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})
