from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app import auth, trees, pomodoro, stats, tree_templates

app = FastAPI(title="Pomodoro Forest API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(trees.router, prefix="/api", tags=["Trees"])
app.include_router(pomodoro.router, prefix="/api", tags=["Pomodoro"])
app.include_router(stats.router, prefix="/api", tags=["User Statistics"])
app.include_router(tree_templates.router, prefix="/api", tags=["Tree Templates"])

# Verificar si estamos en desarrollo local
is_dev = os.environ.get('ENV', 'development') == 'development'

# En desarrollo, servir archivos estáticos del frontend
if is_dev:
    # Ruta al directorio frontend relativa a la ubicación de este archivo
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
    if os.path.isdir(frontend_dir):
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
        
        @app.get("/", include_in_schema=False)
        async def read_index():
            return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/")
async def root():
    return {"message": "Welcome to Pomodoro Forest API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
