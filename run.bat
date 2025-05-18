@echo off
echo ===============================
echo Ejecutando Pomodoro Forest
echo ===============================
echo.

:: Iniciar el servidor backend en una nueva ventana
echo Iniciando el servidor backend...
start cmd /k "cd backend && venv\Scripts\activate && python run.py"

:: Esperar unos segundos para que el servidor inicie
timeout /t 5 /nobreak > nul

:: Abrir el frontend en el navegador predeterminado
echo Abriendo el frontend en su navegador...
start frontend\index.html

echo.
echo ===============================
echo Pomodoro Forest esta en ejecucion!
echo ===============================
echo.
echo * El servidor backend se ejecuta en http://localhost:8000
echo * La interfaz frontend se ha abierto en su navegador
echo.
echo Presione cualquier tecla para detener el servidor cuando termine...
echo.

pause
