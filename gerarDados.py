from os import path 
from sys import argv
from random import randint
class Dados:
    def __init__(self,data:str,hora:str,rua:str,latitude:str,longitude:str):
        self.data = data
        self.hora = hora
        self.rua = rua
        self.latidude = latitude
        self.longitude = longitude
        self.carros = randint(1,30)
        self.motos = randint(1,30)
        self.caminhoes = randint(1,7)
        self.onibus = randint(1,27)
        self.vans = randint(1,18)
        self.total = sum([self.carros,self.motos,self.caminhoes,self.onibus,self.vans])
        
    def __str__(self):
        return """
        {{ 
        "data" : "{}",
        "hora" : "{}",
        "rua" : "{}",
        "latitude" : "{}",
        "longitude" : "{}",
        "carros" : {},
        "motos"  : {},
        "caminhoes" : {},
        "onibus" : {},
        "vans" : {},
        "total" : {}
        }}
        """.format(self.data,self.hora,self.rua,self.latidude,self.longitude,self.carros,self.motos,self.caminhoes,self.onibus,self.vans,self.total)
        
        
        
        
        
        
        
        
        
        
        
        
        
        

"""
[
{ 
"data": "05/12/2024",
"hora": "00:00", 
"rua": "Rua João Gonçalves da Silva", 
"latitude": "-22.4362174", 
"longitude": "-46.8228786", 
"carros": 7, 
"motos": 3, 
"caminhoes": 2, 
"onibus": 0, 
"vans": 1,
"total": 13 

},
{
    .
    .
    .
}, ... 
]
"""
horas = []
for i in range(24):
    horas.append(f"{i:0>2}:00")
    
    
datas = []  
for i in range(1,26):
    datas.append(f"{i:0>2}/06/2025")



def main():
    # if argv.count() > 0:
    RUA = "R. José Germano"
    LATITUDE = "-22.417769"
    LONGITUDE = "-46.820702"
    caminhoArquivo = path.join(path.dirname(__file__),f'{RUA.replace(" ","").replace('.','')}.json')
    with open(caminhoArquivo,'w+') as arquivo:
        arquivo.write('[')
        for data in datas:
            for hora in horas:
                dadoJson = Dados(data,hora,RUA,LATITUDE,LONGITUDE)
                arquivo.write(dadoJson.__str__())
                if datas.index(data) != len(datas) - 1 or horas.index(hora) != len(horas) - 1:
                    arquivo.write(",")
                    # print(f"{data} - {hora}")
        arquivo.write(']')
        
        
main()