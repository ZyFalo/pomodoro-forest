@echo off
echo ===============================
echo Pomodoro Forest - Desarrollo
echo ===============================
echo.

:: Verificar si existe el archivo .env
if not exist .env (
    echo ADVERTENCIA: No se encontró el archivo .env
    echo Creando un archivo temporal desde .env.example...
    copy .env.example .env
    echo Por favor, edita el archivo .env con tus credenciales reales.
    echo.
)

:: Establece las variables de entorno para desarrollo
set ENV=development
set DEBUG=True

:: Activa el entorno virtual e inicia el servidor
echo Iniciando el servidor en modo desarrollo...
cd backend
call venv\Scripts\activate && python run.py

echo.
echo ===============================
echo Servidor detenido
echo ===============================
