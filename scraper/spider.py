import requests
from bs4 import BeautifulSoup
import os
import time
import json
import re  # Importamos expresiones regulares para limpieza avanzada
from urllib.parse import urljoin, urlparse

class BravoSpider:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.dominio = urlparse(base_url).netloc
        self.visitados = set()
        self.por_visitar = [self.base_url]
        self.output_dir = os.path.join("scraper", "data", "json")
        
        # Blacklist de PDFs con errores
        self.blacklist = [
            "https://pascualbravo.edu.co///wp-content/uploads/2019/12/resolucion-227-2010-politica-publica-de-transparencia-administrativa-probidad_compressed-1.pdf",
            "https://pascualbravo.edu.co///wp-content/uploads/2019/12/resolucion-382-24-de-agosto-2010_compressed-1.pdf"
        ]
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def es_valida(self, url):
        url_limpia = url.split('#')[0].rstrip('/')
        if url_limpia in self.blacklist: return False
        parsed = urlparse(url)
        es_interno = parsed.netloc == self.dominio
        no_multimedia = not any(url.lower().endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.gif', '.zip', '.mp4'])
        return es_interno and no_multimedia

    def limpiar_html(self, soup, url):
        """Elimina elementos de interfaz por ID y Clase."""
        es_home = url.lower() == self.base_url.lower() or url.lower() == (self.base_url + "/").lower()
        if not es_home:
            # Header (1245) y Footer (1272)
            for eid in ["1245", "1272"]:
                elem = soup.find("div", {"data-elementor-id": eid})
                if elem: elem.decompose()
            # Botones de Chat
            for chat in soup.find_all("div", class_=["joinchat__button", "joinchat__scroll"]):
                chat.decompose()
            # Basura estándar
            for tag in soup(["script", "style", "aside", "nav", "footer", "header"]):
                tag.decompose()
        return soup

    def extraer_datos(self, soup, url):
        """Extrae metadata y organiza el contenido en párrafos limpios."""
        
        # 1. Buscar Malla Curricular (botón verde de la imagen)
        enlace_malla = "No especificado"
        terminos = ['malla', 'pensum', 'curricular']
        tag_malla = soup.find('a', href=True, string=lambda s: s and any(t in s.lower() for t in terminos))
        if tag_malla:
            enlace_malla = urljoin(self.base_url, tag_malla['href'])

        # 2. PROCESAMIENTO DE PÁRRAFOS
        # Extraemos texto usando salto de línea para separar bloques HTML
        texto_crudo = soup.get_text(separator="\n", strip=True)
        
        # --- Limpieza con Regex ---
        # A. Eliminar espacios en blanco al inicio/final de cada línea
        lineas = [linea.strip() for linea in texto_crudo.split('\n')]
        
        # B. Eliminar líneas vacías duplicadas (dejar máximo un salto entre párrafos)
        texto_unido = "\n".join(lineas)
        # Reemplaza 3 o más saltos de línea por exactamente dos
        texto_final = re.sub(r'\n{3,}', '\n\n', texto_unido)
        # Reemplaza múltiples espacios por uno solo
        texto_final = re.sub(r' +', ' ', texto_final)

        return {
            "metadata": {
                "url": url,
                "titulo": soup.title.string.strip() if soup.title else "Carrera",
                "malla_curricular_link": enlace_malla,
                "fecha": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "contenido": texto_final
        }

    def guardar_json(self, datos):
        nombre = datos['metadata']['url'].replace("https://", "").replace("/", "_").replace(".", "_").strip("_")
        if not nombre or nombre == "pascualbravo_edu_co": nombre = "inicio_home"
        
        ruta = os.path.join(self.output_dir, f"{nombre}.json")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)

    def run(self):
        while self.por_visitar:
            url = self.por_visitar.pop(0)
            if url in self.visitados: continue

            try:
                # Doble verificación de blacklist
                if any(bad in url for bad in self.blacklist): continue

                print(f"Extrayendo contenido de: {url}")
                res = requests.get(url, timeout=15)
                if res.status_code != 200:
                    self.visitados.add(url)
                    continue

                self.visitados.add(url)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                soup_limpia = self.limpiar_html(soup, url)
                datos = self.extraer_datos(soup_limpia, url)
                self.guardar_json(datos)

                for a in soup_limpia.find_all('a', href=True):
                    full_url = urljoin(self.base_url, a['href']).split('#')[0].rstrip('/')
                    if self.es_valida(full_url) and full_url not in self.visitados:
                        self.por_visitar.append(full_url)

                time.sleep(0.7)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    spider = BravoSpider("https://pascualbravo.edu.co")
    spider.run()