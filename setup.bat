@echo off
echo ===============================
echo Configuracion de Pomodoro Forest
echo ===============================
echo.
echo Este script configurara el entorno para ejecutar Pomodoro Forest
echo.

:: Verificar si Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado. Por favor, instale Python 3.8 o superior.
    echo Puede descargarlo desde https://www.python.org/downloads/
    pause
    exit /b
)

:: Crear y activar entorno virtual
echo Creando entorno virtual...
cd backend
python -m venv venv
call venv\Scripts\activate

:: Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo ===============================
echo Configuracion completada!
echo ===============================
echo.
echo Para ejecutar la aplicacion:
echo.
echo 1. Activar el entorno virtual (si no esta activado):
echo    cd backend
echo    venv\Scripts\activate
echo.
echo 2. Iniciar el servidor backend:
echo    python run.py
echo.
echo 3. Abrir el frontend en su navegador:
echo    Abra el archivo frontend/index.html
echo.

pause
