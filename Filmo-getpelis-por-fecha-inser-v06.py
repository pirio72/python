# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 13:10:22 2024

@author: pirio
"""

# Definimos los paquetes que vamos a usar... salvo uno: seleniumbase (más adelante)

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from datetime import timedelta


import time
import re

import requests

start_time = time.time()

'''
NOTA 1: este script originalmente solo funcionaba si se ejecuta desde el Administrador de Archivos
(5/8/2024).

Solución: añadirle, en Tools / Preferences / IPython interpreter, 
  la dirección del intérprete de Python.
En el equipo en el que he hecho esto:
    C:/Users/pirio/AppData/Local/Programs/Python/Python312/python.exe

Y luego, tuve que actualizar Spyder, usando, en el CMD:
    pip install spyder-kernels==2.5.*

    
(Pendiente de resolver)
'''

'''
NOTA 2: se supone que, antes de usar SeleniumBase la primera vez, con Chrome, 
   ha habido que ejecutar este comando, en CMD (Windows):
    
    seleniumbase install chromedriver latest
    
'''

'''
NOTA 3

SeleniumBase funciona principalmente con **selectores CSS**. 

Algunas referencias básicas sobre cómo usarlos:
    - https://seleniumbase.readthedocs.io/en/setup_mkdocs/method_spec/
    - https://github.com/seleniumbase/SeleniumBase/blob/master/examples/my_first_test.py
    - https://github.com/seleniumbase/SeleniumBase/blob/master/help_docs/method_summary.md



En todos ellos, donde pone "self.", puedes cambiarlo por "sb."

'''

'''
NOTA 4

    Usamos como página de ejemplo inicial la página de portada de la Filmoteca
    Española: https://www.cultura.gob.es/cultura/areas/cine/mc/fe/portada.html
    
'''

# Importa selenium base
from seleniumbase import SB

# Crear el prefijo para todos los comandos de selenium
with SB() as sb:
   
    # Abrir una página web: sb.open
    sb.open("http://catalogos.mecd.es/RAFI/cgi-rafi/abnetopac/")
        
    # Hacer clic en un botón/enlace, etc: sb.click
    '''
    
      Aquí (ojo), es un elemento con un atributo (entre corchetes) que tiene un valor.
          los valores se incluye con comilla simple '', pero puede ser doble "".
      Revisar los atributos, qué significan (son OPCIONALES, pero se dejan aquí como ejemplo):
          - timeout: el número de segundos que hay que esperar para que aparezca un elemento,
            si tarda en aparecer.
          - delay: ???
          - scroll: ???
          
    '''
    
    # PASA A LA PÁGINA 2
    sb.click('img[title="Obras audiovisuales"]', timeout=None, delay=0, scroll=True)
    # Nota: en el ejemplo, esto pasa a otra página que es un formulario.
    
    # Escribir texto: sb.type
    # En este caso, en un campo localizado por un selector ('input[name="xsqf01"]'), un texto ('a')
    sb.type('input[name="xsqf01"]', 'a')
    
    # Abrir un campo desplegable y elegir una opción con un texto concreto:
    # select_option_by_text (selector, texto)
    sb.select_option_by_text ('#xssort', 'Fecha de publicación')
    
    # Hacer click sobre un enlace que funciona con un Javascript.
    sb.click('a[onclick="Loading();document.abnform.submit();return false;"]')
    
    # Ahora, estamos en la primera página de RESULTADOS.
    # Entramos en la ficha de la primera película
    sb.click('a[onclick="AbnOpacDoc(1);return false;"]', timeout=10)  
    
    # Cogemos todo el código de la primera página
    
    codigo = sb.get_page_source()
    reg = 50000
    fichero_salida = "ficha-filmoteca-" + str(reg) + ".html"
    # salida = open (fichero_salida, 'w', encoding = "utf-8")
    salida = open (fichero_salida, 'w')
    salida.write(codigo)
    salida.close()
    
    ''' 
    
        ¡¡Y habría que repetir la obtención de código para los 40000 títulos!!
        Vamos a hacer una primera versión con 100 películas.
        
        Duda sobre espacio: ¿hacemos la extracción de los datos al tiempo que descargamos todo el código, por si acaso?
            - Estimación: unos 2GB (registro ejemplo: 44kB)
        
        Duda sobre tiempo: ¿cuánto costará? Tiempos solo para la descarga:
            - 1 sg/película = 40000 sg ~ 11:06:00 (aprox)
            - A partir de ahí, multiplicar por el número de segundos...
            - Tiempo de procesamiento: mucho menor, pero cada segundo son 11 horas más...
            - Idea: descargar y hacer prueba, y estimar.
    
    '''
    
    ## PROCESO PARA ACCEDER A LA PÁGINA SIGUIENTE, EXTRAER EL TEXTO Y GUARDARLO.
    
    while True:
        
        time.sleep(2)
    
        # Y ahora, pasamos a la siguiente página
        sb.click('a[title="Siguiente"]', timeout=10)
        
        codigo = sb.get_page_source()
      
        '''
            # EXTRAER EL NÚMERO DE REGISTRO DE LA PELÍCULA EN LA BASE DE DATOS.
            
            Obtenemos la URL FIJA de cada registro.
            Para ahorrar espacio, vamos a EXTRAER Y GUARDAR, de ella, SOLO EL NÚMERO.
            Las url son de la forma:
                http://catalogos.mecd.es/RAFI/cgi-rafi/abnetopac?TITN=50000
            
            Donde los últimos cinco dígitos son el número de registro,
            que va marcado por el orden de inserción en la base de datos.
                
                
        '''
                
        url_f1 = sb.find_element('div.auth + div + div.titn + a').get_attribute('href')
            
        
        # Extraer el número de código, que está en el rango [54,60] de la url
        reg = url_f1[54:60]
    
        '''
            Como hay registros de cinco cifras y seis cifras:
                - Si tienen seis cifras, nos vale.
                
        '''
        if reg[5] == "%":
           reg = reg[0:5]
    
        # print (reg) 
        
        # Repetimos los pasos para guardar el código de la segunda página
        fichero_salida = "ficha-filmoteca-" + str(reg) + ".html"
        # salida = open (fichero_salida, 'w', encoding = "utf-8")
        salida = open (fichero_salida, 'w')
        salida.write(codigo)
        salida.close()
            
        
        # Para evitar que la ventana se cierre automáticamente al terminar de ejecutarse.
        # input ('?')


end_time = time.time()

total_time = end_time - start_time
print ('Tiempo empleado:', round(end_time - start_time, 2))
print(str(timedelta(seconds=total_time)))


# thours = round ((total_time / 3600), 0)
# tmin = (((total_time - (thours * 3600)) / 60), 0)
# tsec = round (total_time - (thours * 3600) - (tmin * 60))

# print ('Tiempo empleado:', str(thours), ":", str(tmin), ":", str(tsec))
# input ('?')
