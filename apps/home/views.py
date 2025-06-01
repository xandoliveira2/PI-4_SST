# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
import plotly.express as pe
from plotly.offline import plot
import pandas as pd
import pymongo as pm
from .models import Endereco
from django.views.decorators.csrf import csrf_exempt
import json
import os
from django.conf import settings
import requests
from xhtml2pdf import pisa
import matplotlib.pyplot as plt
import io
import base64
from time import sleep

  


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


def tudoNumerico(palavra:str):
    palavra = str(palavra)
    for i in palavra:
        if not i.isdigit():
            return False
    return True

def obter_endereco_por_cep(cep):
    try:
        cep = str(cep)
        if '-' not in cep:
            cep = cep[0:5]+'-'+cep[5:]
        if Endereco.objects.filter(cep=cep).exists(): # consulta o banco de dados antes de consultar a API
            objeto = Endereco.objects.get(cep=cep)
            return objeto.rua
            
        if tudoNumerico(cep):
            url = f"https://viacep.com.br/ws/{cep}/json/"
            resposta = requests.get(url,timeout=10)
        elif '-' in cep:
            cep = cep.replace("-", "")
            url = f"https://viacep.com.br/ws/{cep}/json/"
            resposta = requests.get(url,timeout=10)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            if "erro" in dados:
                return f"CEP {cep} não encontrado."
            try:
                endereco = Endereco(dados.get("logradouro",None),dados.get("bairro",None),dados.get("cep",None))
                try:
                    if Endereco.objects.filter(cep=endereco.cep).exists():
                        return endereco.rua  
                    else:

                        endereco.save()  
                        return endereco.rua  
                except Exception as ex:
                    print(ex)
            except Exception as ex:
                print('erro ao importar a classe endereco...burro')
                return dados.get("logradouro", "Rua não encontrada.")
        else:
            return "Erro ao buscar dados."
    except:
        print('ERRO API')
    
def obter_endereco_delay(cep):
    return obter_endereco_por_cep(cep)
   

def hours_to_decimals_convertion(formato:str):
    """
    formato : horas:minutos:segundos:direção (latitude e longitude)\n
    exemplo: 29°30'29"W\n
    Converte latitude e longitude no formato decimal para aplicar no gráfico de mapa
    que puxa por valores decimais
    """
    if 'S' in formato or 'W' in formato or 'N' in formato or 'E' in formato:

        if 'S' in formato or 'W' in formato:
            negativo = True
        else:
            negativo = False
        formato = formato.replace('S', '').replace('N', '').replace('W', '').replace('E', '')
        try:
            horas = float(formato.split('°')[0])
        except:
            horas = 0.0
        try:
            minutos = float(formato.split('°')[1].split("'")[0])
        except:
            minutos = 0.0
        try:        
            segundos = float(formato.split("'")[1].removesuffix('"'))
        except:
            segundos = 0.0
        decimal = horas + (minutos / 60) + (segundos / 3600)
        if negativo:
            decimal *= -1
        return decimal
    else:
        return formato
def dcolor(value:int|float,valores:list) -> str:
    """Gera o a cor o qual aquele valor será representado no mapa, cujo valores são\n
    definidos pelo usuário em ordem decrescente, ou seja, o primeiro valor\n
    da lista será o vermelho,laranja,amarelo,azul e verde respectivamente\n
    opacidade 55 representado em hexadecimal equivale a 33% de opacidade"""
    if value >= int(valores[0]):
        return '#ff0000'
    elif value >= int(valores[1]):
        return '#ffa500'
    elif value >= int(valores[2]):
        return '#ffff00'
    elif value >= int(valores[3]):
        return '#0000ff'
    else:
        return '#00ff00'

   
    
    
try:    
    client = pm.MongoClient('mongodb://localhost:27017/')
    db = client['pi']
    collection = db['autoflow']
    df = pd.DataFrame(collection.find())
except:
    df = pd.DataFrame()
# df['color'] = df['total'].apply(dcolor)

def aplicarCores(dataframe = df,ParametrosValores=[50,35,25,15]):
    dataframe['color'] = dataframe['total'].apply(lambda value: dcolor(int(value), ParametrosValores))



try:
    df['rua'] = df['rua'].apply(obter_endereco_delay)
    df['latitude_atualizada'] = df['latitude'].apply(hours_to_decimals_convertion)
    df['longitude_atualizada'] = df['longitude'].apply(hours_to_decimals_convertion)
    df['data'] = pd.to_datetime(df['data'],format='%d/%m/%Y') 
    df['data'] = df['data'].dt.strftime('%d/%m/%Y') 
    df['size_column'] = df['total'].apply(lambda x: x if x != 0 else 0.1)
    df = df.sort_values('data')
except: 
    print("Modo de visualização sem dados")
    
    
    
@csrf_exempt
def recebe_data(request):
    if request.method == "POST":
        dados = json.loads(request.body)
        dado_recebido = dados.get('data')
        
        return JsonResponse({'status':'sucesso','dado_recebido':dado_recebido})
    else:
        return JsonResponse({'erro':'Método não permitido'},status=405)


def enviar_coluna_data(request):

    coluna_dados = df['data'].unique().tolist()
   
    return JsonResponse({'dados':coluna_dados})

def enviar_coluna_rua(request):
    data = request.GET.get('param1')
    
    coluna_rua = df[df['data'] == data]['rua'].unique().tolist()

    return JsonResponse({'ruas':coluna_rua})

def enviar_coluna_horarios(request):
    data = request.GET.get('param1')
    horas = df[df['data']==data]['horario'].unique().tolist()
    horas = sorted(horas)
    
    return JsonResponse({'horas':horas})

contadorPagina = 0
def density_map_view(request):
    global contadorPagina
    filtro_data = request.GET.get('param1')
    filtro_hora = request.GET.get('param2')
    filtro_veiculos = request.GET.get('param3', 'carros motos')#('param3', 'carros motos')  # Default para 'carros motos'
    ruas = request.GET.get('ruas')
    ruas = ruas.split(',') if ruas else []
    

    filtro_veiculos = filtro_veiculos.split()
    while '' in filtro_veiculos:
        filtro_veiculos.remove('')
    
    base = ['rua','total'] + filtro_veiculos

    df_filtered1 = df[(df['horario'] == filtro_hora) & (df['data'] == filtro_data)]
    
    
    
    df_filtered1['total'] = 0
    for item in filtro_veiculos:
        df_filtered1['total'] += df_filtered1[item]

    df_filtered1['size_column'] = df_filtered1['total'].apply(lambda x: x if x != 0 else 0.5)
    
    # Aplica cores antes de usar no gráfico
    if 'param4' in request.GET:
        valores = request.GET.get('param4').split('_')
        aplicarCores(df_filtered1, valores)
        data = {
            "vermelho": valores[0],
            "laranja": valores[1],
            "amarelo": valores[2],
            "azul": valores[3],
            "verde": int(valores[3]) - 1
        }
    elif contadorPagina == 0:
        aplicarCores(df_filtered1)
        data = {
            "vermelho": 50,
            "laranja": 35,
            "amarelo": 25,
            "azul": 15,
            "verde": 14
        }
        contadorPagina +=1
    else:
        listaCor = []
        with open('static/cores.json', 'r') as jsonFile:
            data = json.load(jsonFile)
            listaCor.append(int(data["vermelho"]))
            listaCor.append(int(data["laranja"]))
            listaCor.append(int(data["amarelo"]))
            listaCor.append(int(data["azul"]))
        aplicarCores(df_filtered1,listaCor)
    # Salva as cores no arquivo JSON
    file_path = os.path.join(settings.BASE_DIR, 'static', 'cores.json')
    with open(file_path, 'w') as jsonFile:
        json.dump(data, jsonFile, indent=4)
    
    df_filtered1 = df_filtered1[df_filtered1['rua'].isin(ruas)] #<-- essa linha daqui 
    density_map = pe.scatter_mapbox(
        df_filtered1,
        lat='latitude_atualizada',
        lon='longitude_atualizada',
        mapbox_style="carto-darkmatter",
        center={'lat': -22.436491574441884, 'lon': -46.823405867130425},
        zoom=14,
        size='size_column',
        range_color=[10, 60],
        color_continuous_scale='Viridis',
        opacity=0.6,
        custom_data=base,#['rua','total', 'motos', 'carros'],
        color='color',
        color_discrete_map={'#ff0000': 'red', '#00ff00': 'green', '#ffa500': 'orange', '#0000ff': 'blue','#ffff00':'yellow'},
    )

    hover_template_str = ""
    for i, j in enumerate(base):
        hover_template_str += f"{base[i].capitalize()}: %"+"{"+"customdata["+f"{i}"+"]"+"}<br>"
    hover_template_str+='<extra></extra>'
    density_map.update_traces(hovertemplate = hover_template_str)
    density_map.update_layout(showlegend=False)
    grafico_html = plot(density_map,output_type='div')
 
    
    return render(request, 'density_map.html',{'grafico_html':grafico_html})





def pagRelatorio(request):
    return render(request,'relatorio.html')
# views here



def login_view(request):
    return render(request, 'login.html')


def home(request):
    return render(request, 'home.html')



def gerarPDF(request):
    filtro_data = request.GET.get('param1')
    
    rua = request.GET.get('ruas')
    
    
    df_filtrado = df[(df['data'] == filtro_data) & (df['rua'] == rua)]
    def gerar_grafico(dados):
        periodos = dados['periodos']
        carros = dados['carros']
        motos = dados['motos']
        total = [c + m for c, m in zip(carros, motos)]
    
        plt.figure(figsize=(12, 6))
        plt.plot(periodos, carros, marker='o', label='Carros', color='blue')
        plt.plot(periodos, motos, marker='o', label='Motos', color='orange')
        plt.plot(periodos, total, marker='o', label='Total', color='green', linestyle='--')
    
        plt.title('Contagem de Veículos ao Longo do Tempo', fontsize=16)
        plt.xlabel('Períodos', fontsize=14)
        plt.ylabel('Quantidade', fontsize=14)
        plt.xticks(rotation=45, fontsize=10)
        plt.legend(fontsize=12)
        plt.grid(True)
    
        plt.tight_layout()
    
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        grafico_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()
        return grafico_base64



    caminho_logo = os.path.join(settings.BASE_DIR, 'static', 'pdf', 'logo.png')

    with open(caminho_logo, 'rb') as logo_file:
        logo_base64 = base64.b64encode(logo_file.read()).decode('utf-8')
        
        
    # Gerar gráfico
    df_filtrado['horario'] = pd.to_datetime(df_filtrado['horario'], format='%H:%M').dt.time
    
    df_filtrado.sort_values(by='horario', ascending=True , inplace=True)
    df_filtrado['horario'] = df_filtrado['horario'].apply(lambda x: x.strftime('%H:%M'))
    print(df_filtrado)
    print(df_filtrado['horario'].tolist())
    print(df_filtrado['carros'].tolist())
    print(df_filtrado['motos'].tolist() )
    dados_veiculos = {
    'periodos': df_filtrado['horario'].tolist(),  # Converte a coluna 'horario' para uma lista
    'carros': df_filtrado['carros'].tolist(),    # Converte a coluna 'carros' para uma lista
    'motos': df_filtrado['motos'].tolist()       # Converte a coluna 'motos' para uma lista
    }

    grafico_base64 = gerar_grafico(dados_veiculos)

    # Gerar conteúdo HTML com o gráfico
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Contagem de Veículos</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                margin: 20px;
                color: #333;
            }}
            header {{
                text-align: center;
                margin-bottom: 20px;
            }}
            header img {{
                width: 150px;
            }}
            h1 {{
                text-align: center;
                color: #4CAF50;
            }}
            h2 {{
                color: #333;
                margin-top: 20px;
            }}
            p {{
                font-size: 14px;
                line-height: 1.6;
            }}
            ul {{
                font-size: 14px;
                line-height: 1.6;
                margin-left: 20px;
            }}
            li {{
                margin-bottom: 5px;
            }}
            img {{
                display: block;
                margin: 20px auto;
                max-width: 100%;
                height: auto;
            }}
            footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <header>
            <img src="data:image/png;base64,{logo_base64}" alt="Gráfico de Contagem de Veículos">
        </header>
        <h1>Relatório de Contagem de Veículos</h1>
        <p>Este relatório apresenta a contagem de veículos ao longo do tempo, com destaque para carros, motos e o total de veículos.</p>
        <h2>{rua}<h2>
        <ul>
            <li><strong>Total de Carros:</strong> {sum(dados_veiculos['carros'])}</li>
            <li><strong>Total de Motos:</strong> {sum(dados_veiculos['motos'])}</li>
            <li><strong>Total Geral:</strong> {sum(dados_veiculos['carros']) + sum(dados_veiculos['motos'])}</li>
        </ul>
        <img src="data:image/png;base64,{grafico_base64}" alt="Gráfico de Contagem de Veículos">
    </body>
    </html>
    """

    # Gerar o PDF a partir do conteúdo HTML
    pdf_output = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_output)

    if pisa_status.err:
        return HttpResponse("Erro ao gerar o PDF.", status=500)

    # Retornar o PDF gerado como resposta para o download
    pdf_output.seek(0)  # Voltar ao início do arquivo em memória
    response = HttpResponse(pdf_output, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_veiculos.pdf"'

    return response