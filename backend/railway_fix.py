"""
Script de inicialización para Railway.
Este script corrige problemas comunes antes de iniciar la aplicación.
"""

import os
import shutil
import sys
import subprocess

def fix_static_files():
    """Asegura que los archivos estáticos estén en el lugar correcto."""
    print("🔧 Verificando archivos estáticos...")
    
    # Verifica si /app existe (directorio en Railway)
    if os.path.exists("/app"):
        # Verifica si /app/frontend existe
        if not os.path.exists("/app/frontend"):
            print("⚠️ Directorio frontend no encontrado en /app")
            
            # Busca frontend en todas las ubicaciones posibles
            potential_paths = [
                "/app/backend/frontend",
                "/app/frontend",
                "./frontend",
                "../frontend"
            ]
            
            source_path = None
            for path in potential_paths:
                if os.path.exists(path):
                    source_path = path
                    print(f"✅ Frontend encontrado en: {path}")
                    break
            
            # Si encuentra la carpeta frontend en algún lugar, cópiala a /app/frontend
            if source_path:
                print(f"📂 Copiando {source_path} a /app/frontend...")
                try:
                    shutil.copytree(source_path, "/app/frontend")
                    print("✅ Frontend copiado exitosamente")
                except Exception as e:
                    print(f"❌ Error al copiar frontend: {e}")
            else:
                print("❌ No se encontró el directorio frontend en ninguna ubicación")
    else:
        print("ℹ️ No estamos en Railway (no existe /app)")

def fix_env_variables():
    """Asegura que las variables de entorno necesarias estén configuradas."""
    print("🔧 Verificando variables de entorno...")
    
    # Lista de variables de entorno con valores predeterminados
    default_vars = {
        "DEBUG": "False",
        "PORT": "8000",
        "ENV": "production"
    }
    
    for var_name, default_value in default_vars.items():
        if var_name not in os.environ:
            print(f"⚠️ Variable {var_name} no encontrada, estableciendo valor predeterminado: {default_value}")
            os.environ[var_name] = default_value

def main():
    """Función principal que ejecuta todas las correcciones."""
    print("🚀 Iniciando correcciones para Railway...")
    fix_static_files()
    fix_env_variables()
    print("✅ Todas las correcciones completadas.")
    
    # Iniciar uvicorn
    print("🚀 Iniciando la aplicación...")
    port = int(os.environ.get("PORT", 8000))
    cmd = ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(port)]
    subprocess.run(cmd)

if __name__ == "__main__":
    # Cambiar al directorio backend si es necesario
    if not os.path.exists("main.py") and os.path.exists("backend"):
        print("🔄 Cambiando al directorio backend...")
        os.chdir("backend")
    
    main()
