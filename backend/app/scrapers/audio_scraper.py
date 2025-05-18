import requests
import random
import re

def obtener_audio_bosque():
    """
    Extrae la URL del audio de un bosque aleatorio de tree.fm
    con ID entre 40 y 65, sin guardar el HTML.
    """
    # Generar un ID aleatorio para el bosque
    id_bosque = random.randint(40, 65)
    
    # URL de la página web con el sonido del bosque
    url = f"https://www.tree.fm/forest/{id_bosque}"
    
    # Realizar la solicitud a la página web
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            
            # Buscar la URL del audio en el HTML usando expresiones regulares
            pattern = r'<audio[^>]*>.*?<source\s+src="([^"]+\.mp3)"[^>]*>.*?</audio>'
            match = re.search(pattern, response.text, re.DOTALL)
            
            if match:
                return match.group(1)
            
            # Si no se encuentra con la expresión regular anterior, intentar con otra más simple
            pattern2 = r'<source\s+src="([^"]+\.mp3)"'
            match2 = re.search(pattern2, response.text)
            
            if match2:
                return match2.group(1)
        
        return None
    
    except Exception:
        return None

if __name__ == "__main__":
    url_audio = obtener_audio_bosque()
    if url_audio:
        print(url_audio)
    else:
        print("No se pudo encontrar la URL del audio.")
