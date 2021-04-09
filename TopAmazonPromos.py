# Primero se cargan las librerías que se van a usar
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import argparse
import whois
import builtwith
import requests
import re

# Ahora se define la función para obtener el robots.txt
def obt_robot(siteurl):
    if siteurl.endswith('/'):
        path=siteurl
    else:
        path=siteurl+'/'
    req=requests.get(path+'robots.txt',data=None)
    return req.text

# Ahora vamos a guardar el sitio web de amazon para posteriormente obtener los datos del robtos.txt
web = obt_robot('https://www.amazon.com/')

# Obtenemos ahora el robots.txt e imprimimos el resultado
data_robots = re.sub( r'<[^>]*>', ' ', web).strip()
print(data_robots)

# Como se aprecia en el archivo robots.txt, este nos muestra los apartados dentro del sito web para
# los cuales no deberíamos acceder con nuestro proceso de extracción de datos y que se respetarán a lo largo del proyecto

# Ahora se van a identificar las tecnologías presentes detras del sitio web de Amazon
tech_used = builtwith.parse('https://www.amazon.com/')
print(tech_used)

# Luego se van a buscar mas datos sobre el sitio web
w = whois.whois('amazon.com/')
print(w)

# Para realizar la busqueda de datos, primero usamos la librería HTMLSessions para transformar la estructuta
# de los datos y creamos una lista vacía para que posteriomente se puedan agregar las variables capturadas 
lista_de_descuentos = []
x = HTMLSession()

# Ahora se va a empezar a trabajar en función de realizar la extracción de datos del sitio web. Para este proyecto vamos a realizar
# la busqueda de promociones para una marca de computadores, sin embargo,  si es necesario se puede cambiar el item de busqueda.

'''analizar= argparse.ArgumentParser(description='Busqueda de productos y promociones en Amazon')
analizar.add_argument('buscar', metavar='buscar', type=str, help='Por favor escriba el producto que desea buscar. Si el nombre del producto contiene mas de una palabra use + para espaciarlas')
argumentos = analizar.parse_args()
buscar = args.buscar'''


buscar = 'mackbook+pro'
url = f'https://www.amazon.com/s?k={buscar}'

# Con la primera función que se va a crear se podrán acceder a la data del sitio web. Luego usamos sleep para evitar
# el bloqueo del servidor y posteriormente se le hace parseo al sitio por medio de la librería BeatifulSoup
def datos(url):
    y = x.get(url)
    y.html.render(sleep=1)
    soup = BeautifulSoup(y.html.html, 'html.parser')
    return soup

# El siguiente paso consiste en crear la función que nos arroje la lista de los datos especificos que queremos 
# del producto(título, título abreviado, link, precio actual en el caso si es que tiene descuento, precio sin descuento
# críticas, calificación, si es un producto promocionado por amazon a través de amazon choice y la fecha de extracción de los datos)
def descuentos(soup):
# Se crea productos para almacenar allí la data temporal para el bucle
    productos = soup.find_all('div', {'data-component-type':'s-search-result'})
    amazonChoice=False
    for item in productos:
        # Busqueda del nombre completo del producto
        titulo = item.find('a', {'class': 'a-link-normal a-text-normal'}).text.replace(',',' ').strip()
                # Ahora buscamos la etiqueta de amazon choice (Amazon's) para marcar los articulos que la tengan. 
        try:
            if(item.find('span', {'class': 'a-badge-text', 'data-a-badge-color':'sx-cloud'}).text.replace(',',' ').strip() == "Amazon's"):
                 amazonChoice=True
            else:
                amazonChoice=False
        except:
            amazonChoise= False
        # Abreviación del título para mejorar comprensión
        titulo_abreviado = item.find('a', {'class': 'a-link-normal a-text-normal'}).text.replace(',',' ').strip()[:20]
        # Busqueda del link del producto
        link = 'https://www.amazon.com/' + item.find('a', {'class': 'a-link-normal a-text-normal'})['href']
        # Se crea primero una lista llamada lista_spam para verificar si el producto tiene o no descuento
        lista_span = item.find_all('span', {'class': 'a-offscreen'})
        precio_actual, precio_sin_descuento = 0, 0
        if not lista_span:
            print(titulo, "No matches")
        else:
            try:
                precio_actual = float(lista_span[0].text.replace('$','').replace(',','').strip())
                precio_sin_descuento = float(lista_span[1].text.replace('$','').replace(',','').strip())
            except:
                precio_sin_descuento = float(lista_span[0].text.replace('$','').replace(',','').strip())
        # Busqueda de Críticas del producto
        try:
            #criticas = item.find('span', {'class': "a-size-base"}, partial=False).text.strip()
            criticas = float(item.find(lambda tag: tag.name == 'span' and tag.get('class') == ['a-size-base']).text.strip())
        except:
            criticas = 0
        # Busqueda de la calificación en estrellas del producto
        try:
            calificacion = float(item.find('span', {'class': 'a-declarative'}).text.replace(' out of 5 stars','').strip())
        except:
            calificacion = 0
        # Fecha en la cuál fue extraída la información
        date = datetime.datetime.now()
        # Creación de la lista con las varibales obtenidas para cada producto
        articulo_en_venta= {
            'titulo': titulo,
            'titulo_abreviado': titulo_abreviado,
            'link': link,
            'precio_actual': precio_actual,
            'precio_sin_descuento': precio_sin_descuento,
            'criticas': criticas,
            'calificacion': calificacion,  
            'AmazonChoice': amazonChoice,
            'Date':  str(date.day)+'/'+str(date.month)+'/'+str(date.year)    
            }
        lista_de_descuentos.append(articulo_en_venta)
    return



# Posteriormente se crea la función para realizar el salto de página dentro del sitio web de amazon
def siguiente_pagina(soup): 
    # Se realiza la busqueda de las páginas que contienen el producto
    pages = soup.find('ul', {'class': 'a-pagination'})
    # Condicional para continuar la busqueda hasta que encuentre la página final
    if not pages.find('li', {'class': 'a-disabled a-last'}):
        url = 'https://www.amazon.com' + str(pages.find('li', {'class': 'a-last'}).find('a')['href'])
        return url
    else:
        return
# Si la busqueda del prodcuto tiene cientos de p'aginas, se limita a las primeras 20
i=0
while i<20:
    soup = datos(url)
    descuentos(soup)
    url = siguiente_pagina(soup)
    i=i+1
    if not url:
        break
    else:
        print(url)



# Creamos una funcón para generar el dataframe
df = pd.DataFrame(lista_de_descuentos)

# Se calcula el porcentaje de descuento del producto y se ordena de mayor a menor
df['porcentaje_de_descuento'] = 100 - ((df.precio_actual / df.precio_sin_descuento) * 100)
df = df.sort_values(by=['porcentaje_de_descuento'], ascending=False)

# Se crea el archivo csv a partir de la información obtenida y se emite un mensaje de finalización de la ejecución del programa
df.to_csv('TopAmazonPromos.csv', index=False)
print('La busqueda de ' + buscar + ' ha finalizado')





