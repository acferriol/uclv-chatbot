import requests
from bs4 import BeautifulSoup

urls = [
    "https://www.ecured.cu/Universidad_Central_Marta_Abreu_de_Las_Villas",
]

output_file = "datos_universidad.txt"

def scrapear_web():
    full_text = ""
    
    print(f"Iniciando scraping de {len(urls)} páginas...")
    
    for url in urls:
        try:
            print(f"Leyendo: {url}")
            response = requests.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraemos el texto de los párrafos. 
                # Dependiendo de la web, tal vez necesites buscar 'div' con clases específicas.
                paragraphs = soup.find_all('p')
                
                page_text = f"\n\n--- INFORMACIÓN DE: {url} ---\n\n"
                for p in paragraphs:
                    if p.get_text().strip(): # Evitar párrafos vacíos
                        page_text += p.get_text().strip() + "\n"
                
                full_text += page_text
            else:
                print(f"Error {response.status_code} al acceder a {url}")
                
        except Exception as e:
            print(f"Error procesando {url}: {e}")

    # Guardar en archivo
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"Información guardada en {output_file}")

if __name__ == "__main__":
    scrapear_web()