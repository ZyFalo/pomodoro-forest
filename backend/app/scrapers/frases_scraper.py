import requests
from bs4 import BeautifulSoup
import random
import os
import json
import re
from datetime import datetime

def obtener_frase_del_dia():
    """Obtiene una frase motivacional aleatoria de la página web o de la caché"""
    # URL de la página web con frases motivacionales
    url = "https://www.shopify.com/es/blog/frases-de-motivacion"
    
    # Realizar la solicitud a la página web
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Intentar cargar frases desde caché si existe y es del mismo día
        frases_cache = cargar_frases_cache()
        if frases_cache:
            return random.choice(frases_cache)
        
        response = requests.get(url, headers=headers)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Analizar el HTML con BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Inicializar lista para almacenar las frases
            frases = []
            
            # Buscar el artículo principal
            article = soup.find('article')
            
            if article:
                # Buscar elementos de lista numerados que contienen las frases
                list_items = article.select('ol li')
                
                if list_items:
                    for item in list_items:
                        text = item.get_text().strip()
                        # Limpiar el texto
                        text = re.sub(r'\s+', ' ', text)
                        
                        # Si el texto parece una frase motivacional (más de 15 caracteres), lo agregamos
                        if text and len(text) > 15:
                            frases.append(text)
                
                # Si no hay frases, buscar en párrafos con comillas
                if not frases:
                    paragraphs = article.select('p')
                    for p in paragraphs:
                        text = p.get_text().strip()
                        if text and ('"' in text or '"' in text or '"' in text):
                            frases.append(text)
            
            # Si no se encontraron frases, buscar en todo el documento
            if not frases:
                list_items = soup.select('ol li')
                
                for item in list_items:
                    text = item.get_text().strip()
                    text = re.sub(r'\s+', ' ', text)
                    
                    if text and len(text) > 20 and len(text) < 300:
                        frases.append(text)
            
            # Guardar las frases en caché para uso futuro
            if frases:
                guardar_frases_cache(frases)
                return random.choice(frases)
            else:
                return None
        else:
            return None
    
    except Exception:
        # En caso de error, intentar cargar desde caché sin importar la fecha
        frases_cache = cargar_frases_cache(verificar_fecha=False)
        if frases_cache:
            return random.choice(frases_cache)
        
        return None

def cargar_frases_cache(verificar_fecha=True):
    """Carga frases desde el archivo de caché si existe y es del mismo día"""
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frases_cache.json")
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                
                # Verificar si la caché es del mismo día
                if verificar_fecha:
                    fecha_cache = data.get("fecha", "")
                    hoy = datetime.now().strftime("%Y-%m-%d")
                    
                    if fecha_cache != hoy:
                        return None
                
                return data.get("frases", [])
        except Exception:
            pass
    
    return None

def guardar_frases_cache(frases):
    """Guarda las frases en un archivo de caché con la fecha actual"""
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frases_cache.json")
    
    try:
        data = {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "frases": frases
        }
        
        with open(cache_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    
    except Exception:
        pass

# Variable para almacenar las últimas frases devueltas y evitar repeticiones
# Usamos una lista circular de las últimas 5 frases usadas
_ultimas_frases = []
_MAX_FRASES_RECORDADAS = 5

def obtener_frase_aleatoria_siempre():
    """Siempre devuelve una frase aleatoria de las frases cacheadas, evitando repetir las últimas"""
    global _ultimas_frases
    
    frases = cargar_frases_cache(verificar_fecha=False)
    if not frases:
        # Intentar obtener nuevas frases
        frase = obtener_frase_del_dia()
        # Cargar todas las frases
        frases = cargar_frases_cache(verificar_fecha=False)
    
    if frases:
        if len(frases) > 1:
            # Filtrar la lista para quitar las últimas frases usadas y evitar repetición
            frases_disponibles = [f for f in frases if f not in _ultimas_frases]
            if not frases_disponibles:  # Si todas las frases fueron filtradas (caso extremo)
                # Si no hay frases disponibles, usamos la más antigua de las recordadas
                if _ultimas_frases:
                    nueva_frase = _ultimas_frases.pop(0)
                else:
                    nueva_frase = random.choice(frases)
            else:
                # Seleccionar una frase aleatoria entre las disponibles
                nueva_frase = random.choice(frases_disponibles)
            
            # Actualizar la lista circular de últimas frases
            _ultimas_frases.append(nueva_frase)
            if len(_ultimas_frases) > _MAX_FRASES_RECORDADAS:
                _ultimas_frases.pop(0)  # Eliminar la frase más antigua
                
            return nueva_frase
        else:
            # Si solo hay una frase, no hay opción
            return frases[0]
    else:
        return "¡Cada minuto cuenta en tu camino hacia el éxito!"

if __name__ == "__main__":
    # Obtener y mostrar una frase motivacional
    frase = obtener_frase_del_dia()
    if frase:
        print("================================================================================\n")
        print(f"    {frase}\n")
        print("================================================================================")
    else:
        print("No se pudo obtener una frase motivacional.")
