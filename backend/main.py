import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from bson import ObjectId

# Importar componentes adicionales para servir archivos estáticos
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

# Importar tus rutas y modelos
from app import auth, trees, pomodoro, stats

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    print("ADVERTENCIA: MONGO_URI no está configurada. Usando una conexión de respaldo.")
    MONGO_URI = "mongodb://localhost:27017/"

client = MongoClient(MONGO_URI)
db = client["pomodoro_forest"]

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("ADVERTENCIA: SECRET_KEY no está configurada. Usando una clave temporal (no segura para producción).")
    SECRET_KEY = "clave_temporal_no_segura_para_produccion"

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize FastAPI
app = FastAPI(title="Pomodoro Forest API")

# Configurar CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://web-production-8a25d.up.railway.app",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(trees.router, prefix="/api", tags=["Trees"])
app.include_router(pomodoro.router, prefix="/api", tags=["Pomodoro"])
app.include_router(stats.router, prefix="/api", tags=["User Statistics"])

# Sección para servir archivos estáticos - Más robusta
try:
    # Definir posibles localizaciones del frontend
    potential_frontend_paths = [
        "../frontend",          # Relativo al directorio actual
        "../../frontend",       # Un nivel arriba
        "./frontend",           # En el mismo directorio
        "/app/frontend",        # Ruta absoluta en Railway
    ]
    
    # Verificar cada ruta hasta encontrar una válida
    frontend_path = None
    for path in potential_frontend_paths:
        if os.path.exists(path) and os.path.isdir(path):
            frontend_path = path
            print(f"Directorio frontend encontrado en: {path}")
            break
    
    # Si no se encuentra el directorio frontend
    if not frontend_path:
        print("ADVERTENCIA: Directorio frontend no encontrado. Mostrando estructura de directorios:")
        print("Directorio actual:", os.getcwd())
        print("Contenidos:", os.listdir())
        
        # Verificar si estamos en el directorio /app
        if os.path.exists("/app"):
            print("Contenidos de /app:", os.listdir("/app"))
            
            # Si existe /app/frontend, usarlo aunque no se haya detectado antes
            if os.path.exists("/app/frontend"):
                frontend_path = "/app/frontend"
                print("Usando directorio frontend en /app/frontend")
    
    # Si se encontró el directorio frontend, intentar montar archivos estáticos
    if frontend_path:
        # Primero montar los directorios que siempre deberían existir
        app.mount("/css", StaticFiles(directory=f"{frontend_path}/css"), name="css")
        app.mount("/js", StaticFiles(directory=f"{frontend_path}/js"), name="js")
        
        # Luego intentar montar directorios que podrían no existir
        if os.path.exists(f"{frontend_path}/img") and os.path.isdir(f"{frontend_path}/img"):
            app.mount("/img", StaticFiles(directory=f"{frontend_path}/img"), name="img")
        
        # Servir index.html en la ruta raíz
        @app.get("/", response_class=HTMLResponse)
        async def read_index():
            try:
                with open(f"{frontend_path}/index.html", "r", encoding="utf-8") as f:
                    content = f.read()
                return content
            except FileNotFoundError:
                return HTMLResponse(content="<html><body><h1>Pomodoro Forest</h1><p>Error: index.html no encontrado.</p></body></html>")
        
        # Rutas para SPA (Single Page Application)
        @app.get("/{path:path}", response_class=HTMLResponse)
        async def serve_spa(path: str):
            # Rutas de API deben ser manejadas por FastAPI
            if path.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not found")
                
            # Intentar servir el archivo si existe
            file_path = f"{frontend_path}/{path}"
            if os.path.exists(file_path) and not os.path.isdir(file_path):
                try:
                    # Detectar tipo de contenido y servir adecuadamente
                    if file_path.endswith(".html"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        return HTMLResponse(content=content)
                    else:
                        return FileResponse(file_path)
                except Exception as e:
                    print(f"Error sirviendo archivo {file_path}: {e}")
            
            # Si el archivo no existe, servir index.html para SPA routing
            try:
                with open(f"{frontend_path}/index.html", "r", encoding="utf-8") as f:
                    content = f.read()
                return content
            except FileNotFoundError:
                return HTMLResponse(content="<html><body><h1>Pomodoro Forest</h1><p>Error: index.html no encontrado.</p></body></html>")
    else:
        # Si no se encontró el directorio frontend, proporcionar una página básica
        @app.get("/", response_class=HTMLResponse)
        async def root():
            return HTMLResponse(content="<html><body><h1>API de Pomodoro Forest</h1><p>Frontend no encontrado. API disponible en /api.</p></body></html>")

except Exception as e:
    print(f"Error al configurar archivos estáticos: {e}")
    # Proporcionar una página por defecto incluso si hay errores
    @app.get("/", response_class=HTMLResponse)
    async def root_fallback():
        return HTMLResponse(content="<html><body><h1>API de Pomodoro Forest</h1><p>Error al cargar el frontend. La API está disponible en /api.</p></body></html>")

# Root endpoint para la API
@app.get("/api")
async def api_root():
    return {"message": "Welcome to Pomodoro Forest API"}

if __name__ == "__main__":
    import uvicorn
    
    # Obtener puerto y modo debug desde variables de entorno
    port = int(os.getenv("PORT", 8000))
    debug_mode = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # Reload solo en modo debug
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug_mode)
