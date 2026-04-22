import os
import json
import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

os.makedirs("scraper/data", exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extraer_canales_atencion(url_base):
    """
    Visita la pagina principal y extrae unicamente la informacion del pie de pagina (footer)
    donde se encuentran los telefonos, correos y lineas de atencion.
    """
    print("Extrayendo canales de atencion del pie de pagina...")
    try:
        response = httpx.get(url_base, headers=HEADERS, timeout=15.0, follow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        footer = soup.find('footer') or soup.find(attrs={"data-elementor-type": "footer"})
        
        if footer:
            texto_footer = footer.get_text(separator='\n', strip=True)
            
            datos_contacto = {
                "titulo": "Canales de Atencion y Contacto",
                "url_origen": url_base,
                "tipo": "contacto",
                "contenido": texto_footer
            }
            
            with open("scraper/data/canales_atencion.json", "w", encoding="utf-8") as f:
                json.dump(datos_contacto, f, ensure_ascii=False, indent=4)
            print("Canales de atencion guardados correctamente.")
        else:
            print("No se encontro el pie de pagina (footer) en la pagina principal.")
            
    except Exception as e:
        print(f"Error al extraer los canales de atencion: {e}")

def descubrir_programas_desde_tarjetas(url_indice, tipo_categoria):
    """
    Busca los widgets de tarjetas de programas en la pagina especificada.
    Soporta tanto la estructura de Element Pack (usada en Pregrados) 
    como la de JetEngine (usada en Posgrados).
    """
    print(f"Analizando tarjetas de programas en: {url_indice} ({tipo_categoria})")
    programas_encontrados = []
    urls_procesadas = set() 
    
    try:
        response = httpx.get(url_indice, headers=HEADERS, timeout=15.0, follow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar estructura de Pregrados (bdt-interactive-card)
        tarjetas_bdt = soup.find_all('div', class_='bdt-interactive-card')
        for tarjeta in tarjetas_bdt:
            h4_tag = tarjeta.find('h4', class_='bdt-interactive-card-title')
            enlace_tag = tarjeta.find('a', href=True)
            
            if h4_tag and enlace_tag:
                titulo_limpio = h4_tag.get_text(strip=True)
                url_completa = urljoin(url_indice, enlace_tag['href']).split('#')[0].split('?')[0]
                
                if url_completa not in urls_procesadas:
                    programas_encontrados.append({
                        "titulo": titulo_limpio,
                        "url": url_completa,
                        "tipo": tipo_categoria
                    })
                    urls_procesadas.add(url_completa)

        # Buscar estructura de Posgrados (jet-listing-dynamic-link)
        tarjetas_jet = soup.find_all('h3', class_='jet-listing-dynamic-link')
        for tarjeta in tarjetas_jet:
            enlace_tag = tarjeta.find('a', class_='jet-listing-dynamic-link__link', href=True)
            
            if enlace_tag:
                # El titulo real del programa se encuentra dentro de un span con esta clase
                span_label = enlace_tag.find('span', class_='jet-listing-dynamic-link__label')
                titulo_limpio = span_label.get_text(strip=True) if span_label else enlace_tag.get_text(strip=True)
                
                url_completa = urljoin(url_indice, enlace_tag['href']).split('#')[0].split('?')[0]
                
                if url_completa not in urls_procesadas:
                    programas_encontrados.append({
                        "titulo": titulo_limpio,
                        "url": url_completa,
                        "tipo": tipo_categoria
                    })
                    urls_procesadas.add(url_completa)
                
        print(f"Se encontraron {len(programas_encontrados)} programas de {tipo_categoria}.")
        return programas_encontrados

    except Exception as e:
        print(f"Error al escanear el indice {url_indice}: {e}")
        return []

def extraer_metadatos_por_patrones(texto):
    """
    Busca informacion clave en el texto crudo usando patrones comunes,
    sin depender de la estructura HTML.
    """
    metadatos = {}
    patrones = {
        "snies": r"(?i)snies[\s:]*([0-9]+)",
        "duracion": r"(?i)duraci[oó]n[\s:]*([a-zA-Z0-9\s]+(?:semestres|años|niveles))",
        "modalidad": r"(?i)modalidad[\s:]*([a-zA-Z\s]+)",
        "titulo_otorga": r"(?i)t[ií]tulo que otorga[\s:]*([a-zA-Z\s]+)(?:\n|$)",
        "creditos": r"(?i)cr[eé]ditos[\s:]*([0-9]+)"
    }
    
    for clave, patron in patrones.items():
        coincidencia = re.search(patron, texto)
        if coincidencia:
            valor = coincidencia.group(1).strip()
            if len(valor) < 100: 
                metadatos[clave] = valor
                
    return metadatos

def scrape_programa_robusto(datos_pagina):
    """
    Extrae el contenido de un programa de forma robusta, ignorando el HTML 
    especifico y centrandose en el texto renderizado.
    """
    url = datos_pagina["url"]
    tipo = datos_pagina["tipo"]
    titulo_ref = datos_pagina["titulo"]
    
    print(f"Procesando [{tipo}]: {titulo_ref}")
    
    try:
        response = httpx.get(url, headers=HEADERS, timeout=15.0, follow_redirects=True)
        response.raise_for_status() 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Limpieza radical: eliminamos encabezado, pie de pagina, menus y scripts
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'form']):
            tag.decompose()
            
        # Eliminamos contenedores especificos del footer y menus de Elementor
        for tag in soup.find_all(attrs={"data-elementor-type": ["footer", "header"]}):
            tag.decompose()
            
        # Obtenemos todo el texto limpio que quedo en la pagina
        # Separamos con saltos de linea dobles para mantener la legibilidad
        texto_limpio = soup.get_text(separator='\n\n', strip=True)
        
        # Limpiamos multiples saltos de linea consecutivos
        texto_limpio = re.sub(r'\n{3,}', '\n\n', texto_limpio)
        
        if not texto_limpio.strip():
            print(f"Advertencia: No se extrajo texto de {url}")
            return

        # Intentamos extraer la ficha tecnica buscando palabras en el texto
        metadatos = extraer_metadatos_por_patrones(texto_limpio)

        ruta_url = urlparse(url).path.strip('/')
        filename = ruta_url.replace('/', '_') or titulo_ref.lower().replace(' ', '_')

        datos_estructurados = {
            "titulo": titulo_ref,
            "url_origen": str(response.url),
            "tipo": tipo,
            "metadatos_identificados": metadatos,
            "contenido": texto_limpio
        }
        
        filepath = f"scraper/data/{filename}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(datos_estructurados, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        print(f"Error al extraer {url}: {e}")


if __name__ == "__main__":
    print("\n--- EXTRACCION DE CANALES DE ATENCION ---")
    extraer_canales_atencion("https://pascualbravo.edu.co/")
    
    print("\n--- DESCUBRIMIENTO DE PROGRAMAS ---")
    directorios_programas = [
        {"url": "https://pascualbravo.edu.co/pregrados/", "tipo": "pregrado"},
        {"url": "https://pascualbravo.edu.co/posgrados/", "tipo": "posgrado"}
    ]
    
    lista_programas = []
    for directorio in directorios_programas:
        lista_programas.extend(descubrir_programas_desde_tarjetas(directorio["url"], directorio["tipo"]))
        
    print(f"\n--- EXTRACCION DE CONTENIDO ({len(lista_programas)} programas) ---")
    for programa in lista_programas:
        scrape_programa_robusto(programa)
        
    print("\nProceso finalizado. Revisa la carpeta scraper/data/")