from app.scraper.extractor import (
    extraer_canales_atencion,
    descubrir_programas_desde_tarjetas,
    scrape_programa_robusto
)

def run_pipeline():

    print("Paso 1: Canales de atención")

    extraer_canales_atencion(
        "https://pascualbravo.edu.co/"
    )

    print("Paso 2: Descubrir programas")

    directorios = [
        {
            "url": "https://pascualbravo.edu.co/pregrados/",
            "tipo": "pregrado"
        },
        {
            "url": "https://pascualbravo.edu.co/posgrados/",
            "tipo": "posgrado"
        }
    ]

    programas = []

    for d in directorios:

        encontrados = descubrir_programas_desde_tarjetas(
            d["url"],
            d["tipo"]
        )

        programas.extend(encontrados)

    print("Paso 3: Extraer contenido")

    for programa in programas:

        scrape_programa_robusto(programa)

    print("Pipeline terminado")


if __name__ == "__main__":

    run_pipeline()