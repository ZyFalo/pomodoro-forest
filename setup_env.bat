@echo off
echo ===============================
echo Configuración de variables de entorno
echo ===============================
echo.

if exist .env (
    echo El archivo .env ya existe.
    echo Si quieres crearlo de nuevo, elimina el archivo actual primero.
) else (
    echo Creando archivo .env desde plantilla...
    copy .env.example .env
    echo.
    echo IMPORTANTE: Edita el archivo .env para configurar tus credenciales reales!
    echo.
)

echo Presiona cualquier tecla para continuar...
pause >nul
