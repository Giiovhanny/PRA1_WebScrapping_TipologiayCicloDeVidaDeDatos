from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import datetime


lista_de_descuentos = []
x = HTMLSession()

buscador = 'smart+phone'
url = f'https://www.amazon.com/s?k={buscador}&i=computers'
#url=f'https://www.amazon.com/s?k=headphones&crid=1FTNYIJXTM4XJ&sprefix=head%2Caps%2C266&ref=nb_sb_ss_ts-doa-p_1_4'


def datos(url):
    y = x.get(url)
    y.html.render(sleep=1)
    soup = BeautifulSoup(y.html.html, 'html.parser')
    return soup

def descuentos(soup):
    productos = soup.find_all('div', {'data-component-type':'s-search-result'})
    amazonChoice=False
    for item in productos:
        titulo = item.find('a', {'class': 'a-link-normal a-text-normal'}).text.replace(',',' ').strip()
        # Ahora buscamos la etiqueta de amazon choice (Amazon's) para marcar los articulos que la tengan. 
        try:
            if(item.find('span', {'class': 'a-badge-text', 'data-a-badge-color':'sx-cloud'}).text.replace(',',' ').strip() == "Amazon's"):
                 amazonChoice=True
            else:
                amazonChoice=False
        except:
            amazonChoise= False

        titulo_abreviado = item.find('a', {'class': 'a-link-normal a-text-normal'}).text.replace(',',' ').strip()[:20]
        link = item.find('a', {'class': 'a-link-normal a-text-normal'})['href']
        # REVISAR ESTE PRIMER TRY AND EXCEPT
        spanlist = item.find_all('span', {'class': 'a-offscreen'})
        precio_actual, precio_sin_descuento = 0, 0
        if not spanlist:
            print(titulo, "No matches")
        else:
            try:
                precio_actual = float(spanlist[0].text.replace('$','').replace(',','').strip())
                precio_sin_descuento = float(spanlist[1].text.replace('$','').replace(',','').strip())
            except:
                precio_sin_descuento = float(spanlist[0].text.replace('$','').replace(',','').strip())
        try:
            #criticas = item.find('span', {'class': "a-size-base"}, partial=False).text.strip()
            criticas = float(item.find(lambda tag: tag.name == 'span' and tag.get('class') == ['a-size-base']).text.strip())
        except:
            criticas = 0
        try:
            calificacion = float(item.find('span', {'class': 'a-declarative'}).text.replace(' out of 5 stars','').strip())
        except:
            calificacion = 0
        date = datetime.datetime.now()
        
        
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

def siguiente_pagina(soup): 
    pages = soup.find('ul', {'class': 'a-pagination'})   
    if not pages.find('li', {'class': 'a-disabled a-last'}):
        url = 'https://www.amazon.com' + str(pages.find('li', {'class': 'a-last'}).find('a')['href'])
        return url
    else:
        return

i=0
while i<3:
    soup = datos(url)
    descuentos(soup)
    url = siguiente_pagina(soup)
    i=i+1
    if not url:
        break
    else:
        print(url)
        #print(len(lista_de_descuentos))
# while True:
#     soup = datos(url)
#     descuentos(soup)
#     url = siguiente_pagina(soup)
#     if not url:
#         break
#     else:
#         print(url)
#         print(len(lista_de_descuentos))


df = pd.DataFrame(lista_de_descuentos)
df['porcentaje_de_descuento'] = 100 - ((df.precio_actual / df.precio_sin_descuento) * 100)
df = df.sort_values(by=['porcentaje_de_descuento'], ascending=False)
df.to_csv(buscador + 'descuentos_encontrados_giovanny333.csv', index=False)
print('Fin.')