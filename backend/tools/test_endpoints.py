#!/usr/bin/env python3
# filepath: c:\Users\User\Desktop\Proyecto Final Distribuidos\backend\tools\test_endpoints.py
"""
Script para probar todos los endpoints de la API Pomodoro Forest y generar documentación.

Ejecutar desde la raíz del proyecto:
python backend/tools/test_endpoints.py

Flags disponibles:
--output=markdown  # Guarda la salida como README_API.md
--verbose          # Muestra información detallada de cada solicitud
--filter=auth      # Solo prueba endpoints que contienen "auth" en la ruta
"""

import os
import sys
import json
import time
import argparse
import requests
import datetime
from pathlib import Path
from termcolor import colored
from collections import defaultdict

# Configuración
API_PREFIX = "/api"
BASE_URL = "http://localhost:8000"

OUTPUT_DIR = Path("docs")
MARKDOWN_FILE = OUTPUT_DIR / "API_DOCUMENTATION.md"
SUCCESS_COLOR = "green"
ERROR_COLOR = "red"
INFO_COLOR = "blue"
WARNING_COLOR = "yellow"

# Credenciales de prueba
TEST_USER = {
    "username": "test_user_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
    "password": "test_password123",
    "email": "test@example.com"
}

# Estado global
access_token = None
test_stats = {
    "total": 0,
    "success": 0,
    "failed": 0,
    "skipped": 0
}
results = []
created_data = {}  # Almacena IDs y otros datos creados durante las pruebas

def parse_args():
    """Analiza los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description='Prueba los endpoints de la API Pomodoro Forest')
    parser.add_argument('--output', choices=['console', 'markdown', 'json', 'both'], default='both', 
                        help='Formato de salida (por defecto: both)')
    parser.add_argument('--verbose', action='store_true', help='Mostrar información detallada')
    parser.add_argument('--filter', type=str, help='Filtrar endpoints que contengan este texto')
    return parser.parse_args()

def print_header(text):
    """Imprime un encabezado formateado."""
    print("\n" + colored("=" * 80, INFO_COLOR))
    print(colored(f" {text} ".center(80), INFO_COLOR))
    print(colored("=" * 80, INFO_COLOR))

def print_result(success, endpoint, method, status_code, message="", response_data=None, elapsed=0):
    """Imprime el resultado de una prueba."""
    color = SUCCESS_COLOR if success else ERROR_COLOR
    result_text = "✓ ÉXITO" if success else "✗ ERROR"
    
    print(f"{colored(result_text, color)} [{method}] {endpoint} - {status_code} ({elapsed:.2f}ms)")
    
    if message:
        print(f"  {colored(message, INFO_COLOR)}")
    
    # Actualizar estadísticas
    test_stats["total"] += 1
    if success:
        test_stats["success"] += 1
    else:
        test_stats["failed"] += 1
    
    # Guardar resultado para la documentación
    result_data = {
        "success": success,
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "message": message,
        "response": response_data,
        "elapsed": elapsed
    }
    results.append(result_data)
    return result_data

def make_request(method, endpoint, expected_status=200, auth=False, json_data=None, files=None, params=None):
    """Realiza una solicitud HTTP a un endpoint."""
    # Asegurarse que el endpoint tenga el prefijo correcto
    if not endpoint.startswith(API_PREFIX):
        endpoint = f"{API_PREFIX}{endpoint}"
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    
    if auth and access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            if endpoint.endswith('/token'):
                # Caso especial para autenticación: usar form-data en lugar de JSON
                headers.pop('Content-Type', None)  # Quitar Content-Type para usar form-data
                response = requests.post(url, headers=headers, data=params)  # Usar params como form-data
            elif files:
                response = requests.post(url, headers=headers, data=json_data, files=files)
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=json_data)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            response = requests.put(url, headers=headers, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return print_result(False, endpoint, method, 0, f"Método no soportado: {method}")
        
        elapsed = (time.time() - start_time) * 1000  # ms
        
        # Intentar obtener respuesta JSON, si falla usar texto
        try:
            # Verifica si hay contenido antes de intentar decodificar JSON
            response_data = response.json() if response.content.strip() else {}
        except:
            response_data = {"text": response.text}
        
        success = response.status_code == expected_status
        message = f"Respuesta esperada: {expected_status}, Recibida: {response.status_code}"
        
        if not success:
            message += f"\nError: {response.text}"
        
        return print_result(success, endpoint, method, response.status_code, message, response_data, elapsed), response
    
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000  # ms
        return print_result(False, endpoint, method, 0, f"Error al hacer la solicitud: {str(e)}", elapsed=elapsed), None

def test_auth_endpoints():
    """Prueba los endpoints de autenticación."""
    global access_token
    
    print_header("Prueba de Endpoints de Autenticación")
    
    # Registro de usuario
    result, response = make_request("POST", "/register", 200, False, TEST_USER)
    
    # Login
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    result, response = make_request("POST", "/token", 200, False, None, None, login_data)
    
    if result["success"] and response:
        access_token = response.json().get("access_token")
        print(f"  Token obtenido: {colored('✓', SUCCESS_COLOR)}")
    else:
        print(f"  {colored('No se pudo obtener token de acceso - algunas pruebas fallarán', WARNING_COLOR)}")

def test_pomodoro_endpoints():
    """Prueba los endpoints del Pomodoro."""
    print_header("Prueba de Endpoints de Pomodoro")
    
    # Iniciar pomodoro
    result, response = make_request("POST", "/start-pomodoro", 200, True, {"duration": 5})
    
    # Obtener frase motivacional
    result, response = make_request("GET", "/motivational-phrase", 200, True)
    
    # Completar pomodoro
    result, response = make_request("POST", "/complete-pomodoro", 200, True)
    
    if result["success"] and response and "tree" in response.json():
        tree_id = response.json()["tree"]["id"]
        created_data["tree_id"] = tree_id
        print(f"  Árbol creado con ID: {tree_id}")

def test_tree_endpoints():
    """Prueba los endpoints de árboles."""
    print_header("Prueba de Endpoints de Árboles")
    
    # Obtener lista de árboles
    result, response = make_request("GET", "/trees", 200, True)
    
    if not result["success"]:
        print(f"  {colored('No se pudieron obtener árboles, omitiendo pruebas relacionadas', WARNING_COLOR)}")
        return
    
    tree_id = created_data.get("tree_id")
    if not tree_id and response and response.json():
        trees = response.json()
        if trees and len(trees) > 0:
            tree_id = trees[0].get("id")
            created_data["tree_id"] = tree_id
    
    if tree_id:
        # Actualizar árbol
        tree_data = {
            "name": "Árbol de Prueba Actualizado",
            "category": "Prueba",
            "description": "Árbol utilizado para pruebas de API",
            "image_url": "https://example.com/tree.jpg"
        }
        result, _ = make_request("PUT", f"/trees/{tree_id}", 200, True, tree_data)
        
        # Eliminar árbol - este debe ser el último test sobre este árbol
        result, _ = make_request("DELETE", f"/trees/{tree_id}", 200, True)
    else:
        print(f"  {colored('No hay ID de árbol disponible para pruebas', WARNING_COLOR)}")
        test_stats["skipped"] += 2

def test_stats_endpoints():
    """Prueba los endpoints de estadísticas."""
    print_header("Prueba de Endpoints de Estadísticas")
    
    # Obtener estadísticas
    result, _ = make_request("GET", "/user/stats", 200, True)
    
    # Actualizar estadísticas
    stats_data = {
        "pomodoros_completed": 1,
        "total_focus_minutes": 25
    }
    result, _ = make_request("POST", "/user/stats/update", 200, True, stats_data)

def test_tree_template_endpoints():
    """Prueba los endpoints de plantillas de árboles (admin)."""
    print_header("Prueba de Endpoints de Plantillas de Árboles (Admin)")
    
    # Nota: Estos endpoints requieren permisos de administrador
    # pero los probamos de todos modos para documentación
    
    # Obtener plantillas de árboles
    result, _ = make_request("GET", "/admin/tree-templates", 401, True)
    
    # Los siguientes endpoints requieren permisos de admin, por lo que es normal que fallen
    test_stats["skipped"] += 3

def generate_markdown():
    """Genera documentación en formato Markdown."""
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)
    
    with open(MARKDOWN_FILE, "w", encoding="utf-8") as f:
        f.write("# Documentación de API Pomodoro Forest\n\n")
        f.write("*Generado automáticamente el " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*\n\n")
        
        f.write("## Resumen de pruebas\n\n")
        f.write("| Categoría | Total | Exitosas | Fallidas | Omitidas |\n")
        f.write("|-----------|-------|----------|----------|----------|\n")
        f.write(f"| **Total** | {test_stats['total']} | {test_stats['success']} | {test_stats['failed']} | {test_stats['skipped']} |\n\n")
        
        # Agrupar por categorías
        endpoints_by_category = defaultdict(list)
        for result in results:
            path = result["endpoint"].split("/")
            if len(path) > 1:
                category = path[1]
            else:
                category = "otros"
            endpoints_by_category[category].append(result)
        
        for category, endpoints in endpoints_by_category.items():
            f.write(f"## Endpoints de {category.capitalize()}\n\n")
            
            for endpoint in endpoints:
                method = endpoint["method"]
                path = endpoint["endpoint"]
                status = endpoint["status_code"]
                success = "✓" if endpoint["success"] else "✗"
                
                f.write(f"### {method} {path}\n\n")
                f.write(f"**Estado:** {success} {status}\n\n")
                
                if endpoint.get("message"):
                    f.write(f"**Mensaje:** {endpoint['message']}\n\n")
                
                if endpoint.get("response"):
                    f.write("**Respuesta:**\n\n")
                    f.write("```json\n")
                    f.write(json.dumps(endpoint["response"], indent=2))
                    f.write("\n```\n\n")
                
                if endpoint.get("elapsed"):
                    f.write(f"**Tiempo de respuesta:** {endpoint['elapsed']:.2f}ms\n\n")
                
        f.write("\n## Notas\n\n")
        f.write("* Las pruebas se realizaron contra un servidor local en `http://localhost:8000`\n")
        f.write("* Algunos endpoints pueden requerir permisos adicionales\n")
        f.write("* Esta documentación es generada automáticamente y puede no reflejar cambios recientes en la API\n")
    
    print(f"\nDocumentación generada en: {MARKDOWN_FILE}")

def save_json_results():
    """Guarda los resultados en formato JSON."""
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)
    
    # Guardar resultados en JSON para generar documentación HTML
    json_path = OUTPUT_DIR / "api_test_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResultados guardados en: {json_path}")

def print_summary():
    """Imprime un resumen de las pruebas."""
    print_header("Resumen de Pruebas")
    
    total = test_stats["total"]
    success = test_stats["success"]
    failed = test_stats["failed"]
    skipped = test_stats["skipped"]
    
    success_rate = (success / total * 100) if total > 0 else 0
    
    print(f"Total de pruebas: {total}")
    print(f"Exitosas: {colored(success, SUCCESS_COLOR)} ({success_rate:.1f}%)")
    print(f"Fallidas: {colored(failed, ERROR_COLOR)}")
    print(f"Omitidas: {colored(skipped, WARNING_COLOR)}")
    
    print("\nPara generar documentación detallada:")
    print(colored("  python backend/tools/test_endpoints.py --output=markdown", INFO_COLOR))

def main():
    """Función principal."""
    args = parse_args()
    
    print_header("Prueba de API Pomodoro Forest")
    print(f"URL base: {BASE_URL}")
    print(f"Usuario de prueba: {TEST_USER['username']}")
    
    # Ejecutar pruebas
    test_auth_endpoints()
    test_pomodoro_endpoints()
    test_tree_endpoints()
    test_stats_endpoints()
    test_tree_template_endpoints()
    
    # Resumen
    print_summary()
    
    # Generar salidas solicitadas
    if args.output in ["markdown", "both"]:
        generate_markdown()
    
    if args.output in ["json", "both"]:
        save_json_results()

if __name__ == "__main__":
    # Asegurarse de que estamos en la raíz del proyecto
    if not Path("backend").exists() or not Path("frontend").exists():
        print(colored("Error: Ejecuta este script desde la raíz del proyecto", ERROR_COLOR))
        sys.exit(1)
    
    main()