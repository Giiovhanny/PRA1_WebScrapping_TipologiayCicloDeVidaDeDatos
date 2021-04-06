from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import argparse


lista_de_descuentos = []
x = HTMLSession()

buscador = 'laptop+asus+a15'
url = f'https://www.amazon.com/s?k={buscador}&i=computers'


def datos(url):
    y = x.get(url)
    y.html.render(sleep=2)
    soup = BeautifulSoup(y.html.html, 'html.parser')
    return soup

def descuentos(soup):
    productos = soup.find_all('div', {'data-component-type': 's-search-result'})
    for item in productos:
        titulo = item.find('a', {'class': 'a-link-normal a-text-normal'}).text.strip()
        titulo_abreviado = item.find('a', {'class': 'a-link-normal a-text-normal'}).text.strip()[:20]
        link = item.find('a', {'class': 'a-link-normal a-text-normal'})['href']
        # REVISAR ESTE PRIMER TRY AND EXCEPT
        try:
            precio_actual = float(item.find_all('span', {'class': 'a-offscreen'})[0].text.replace('$','').replace(',','').strip())
            precio_sin_descuento = float(item.find_all('span', {'class': 'a-offscreen'})[1].text.replace('$','').replace(',','').strip())
        except:
            #precio_sin_descuento = float(item.find('span', {'class': 'a-offscreen'}).text.replace('$','').replace(',','').strip())
            precio_sin_descuento = float(item.find('span', {'class': 'a-offscreen'}))
        try:
            criticas = float(item.find('span', {'class': 'a-size-base'}).text.strip())
        except:
            criticas = 0
        try:
            calificacion = float(item.find('span', {'class': 'a-declarative'}).text.replace(' out of 5 stars','').strip())
        except:
            calificacion = 0
        
        articulo_en_venta= {
            'titulo': titulo,
            'titulo_abreviado': titulo_abreviado,
            'link': link,
            'precio_actual': precio_actual,
            'precio_sin_descuento': precio_sin_descuento,
            'criticas': criticas,
            'calificacion': calificacion       
            }
        lista_de_descuentos.append(articulo_en_venta)
    return

def siguiente_pagina(soup): 
    pages = soup.find('ul', {'class': 'a-pagination'})   
    if not pages.find('li', {'class': 'a-disabled a-last'}):
        url = 'https://www.amazon.com' + str(pages.find('li', {'class': 'a-last'}).find('a')['href'])
        return url
    else:
        return

while True:
    soup = datos(url)
    descuentos(soup)
    url = siguiente_pagina(soup)
    if not url:
        break
    else:
        print(url)
        print(len(lista_de_descuentos))


df = pd.DataFrame(lista_de_descuentos)
df['porcentaje_de_descuento'] = 100 - ((df.precio_actual / df.precio_sin_descuento) * 100)
df = df.sort_values(by=['porcentaje_de_descuento'], ascending=False)
df.to_csv(buscador + 'descuentos_encontrados.csv', index=False)
print('Fin.')