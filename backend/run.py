import os
import uvicorn

if __name__ == "__main__":
    # Obtener el puerto de Railway o usar 8000 como valor predeterminado
    port = int(os.getenv("PORT", 8000))
    # Ejecutar la aplicación
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
