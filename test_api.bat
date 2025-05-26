REM filepath: c:\Users\User\Desktop\Proyecto Final Distribuidos\test_api.bat
@echo off
echo =======================================
echo  Prueba y Documentación de API
echo =======================================

REM Instalar dependencias necesarias
echo Instalando dependencias...
pip install termcolor
echo.

REM Crear directorio para documentación si no existe
if not exist docs mkdir docs

echo.
echo 1. Ejecutando pruebas de endpoints...
python backend/tools/test_endpoints.py --output=json

echo.
echo 2. Generando documentación HTML interactiva...
python backend/tools/generate_api_docs.py

echo.
echo =======================================
echo Documentación generada en:
echo - docs\API_DOCUMENTATION.md  (Markdown)
echo - docs\api_documentation.html (HTML interactivo)
echo =======================================
echo.
echo Presiona cualquier tecla para abrir la documentación HTML en tu navegador...
pause > nul

start docs\api_documentation.html