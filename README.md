# Pomodoro Forest 🌲⏱️

Pomodoro Forest es una aplicación web que combina la técnica Pomodoro con sonidos de bosque y frases motivacionales, además de un pequeño "juego" para coleccionar árboles al terminar cada sesión.

## Características 🌟

- **Técnica Pomodoro**: Temporizador configurable para gestionar tu tiempo de trabajo.
- **Ambientes sonoros**: Cada sesión incluye sonidos relajantes de bosque.
- **Frases motivacionales**: Frases aleatorias para mantenerte motivado durante tus sesiones.
- **Colección de árboles**: Gana un árbol único por cada sesión completada.
- **Inventario personal**: Gestiona y visualiza tu bosque virtual.

## Tecnologías 💻

### Backend
- **Python + FastAPI**: API REST con validación y documentación automática.
- **MongoDB Atlas**: Base de datos en la nube para almacenar usuarios y árboles.
- **JWT**: Gestión de sesión de usuario mediante tokens.
- **Web Scraping**: Extracción de sonidos de bosque y frases motivacionales.
- **Pytest**: Tests automatizados para asegurar la funcionalidad.

### Frontend
- **HTML, CSS y JavaScript**: Interfaz limpia y receptiva.
- **Bootstrap 5**: Estilos modernos y componentes interactivos.
- **Fetch API**: Comunicación asíncrona con el backend.

## Instalación y ejecución ⚙️

### Requisitos previos
- Python 3.8 o superior
- MongoDB Atlas (o MongoDB local)

### Configuración de variables de entorno

1. Crea un archivo `.env` en la raíz del proyecto basado en `.env.example`:
   ```bash
   # Usa el script proporcionado
   setup_env.bat
   
   # O copia manualmente
   copy .env.example .env
   ```

2. Edita el archivo `.env` con tus credenciales reales:
   ```
   # MongoDB - Tu URI de conexión
   MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/pomodoro_forest
   
   # JWT - Genera una clave secreta segura
   SECRET_KEY=clave_secreta_jwt_aleatoria_larga
   
   # Configuración
   DEBUG=False
   PORT=8000
   ```

3. El archivo `.env` está incluido en `.gitignore` para proteger tus credenciales
- Navegador web moderno

### Backend

1. Navega al directorio del backend:
```
cd backend
```

2. Instala las dependencias:
```
pip install -r requirements.txt
```

3. Configura las variables de entorno (crea un archivo .env con estas variables):
```
MONGODB_URI=tu_url_de_mongodb
SECRET_KEY=tu_clave_secreta_para_jwt
```

4. Ejecuta el servidor:
```
python run.py
```

### Frontend

1. Simplemente abre los archivos HTML en tu navegador o utiliza un servidor web simple:
```
cd frontend
python -m http.server
```

2. Abre http://localhost:8000 en tu navegador.

## Instrucciones para ejecutar el proyecto

### Desarrollo local (recomendado)

La forma más fácil es usar el script automatizado:

```cmd
# En la raíz del proyecto:
dev_server.bat
```

Este script:
1. Crea automáticamente el archivo .env si no existe
2. Configura el modo de desarrollo
3. Inicia el servidor backend que también sirve los archivos frontend

La aplicación estará disponible en: http://localhost:8000

### Ejecución manual

Si prefieres control manual, sigue estos pasos:

```cmd
# En la raíz del proyecto:
setup_env.bat  # Crea el archivo .env si no existe

cd backend
venv\Scripts\activate
python run.py
```

## Despliegue en Railway 🚀

Este proyecto está configurado para ser desplegado en Railway:

1. Conecta tu repositorio de GitHub a Railway
2. Railway detectará automáticamente la configuración necesaria gracias al Procfile
3. Asegúrate de configurar las variables de entorno en Railway:
   - MONGO_URI
   - SECRET_KEY
   - DEBUG=False

## Autores 👥

[Tu nombre o equipo aquí]

## Licencia 📜

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.
```
pip install -r requirements.txt
```

5. Ejecuta el servidor:
```
python run.py
```

El servidor estará disponible en `http://localhost:8000`

### Frontend

1. Simplemente abre el archivo `index.html` en tu navegador:
```
cd "c:\Users\User\Desktop\Proyecto Final Distribuidos\frontend"
```

2. (Opcional) Puedes usar un servidor estático ligero:
```
npx serve
```

## Uso

1. Regístrate o inicia sesión en la aplicación.
2. Configura la duración de tu sesión Pomodoro (por defecto: 25 minutos).
3. Haz clic en "Iniciar" para comenzar el temporizador.
4. Trabaja enfocado mientras escuchas los sonidos relajantes del bosque.
5. ¡Al finalizar, recibirás un árbol único para tu colección!
6. Visita "Mi Bosque" para ver y gestionar tus árboles ganados.

## Estructura del proyecto

```
proyecto/
├── backend/
│   ├── app/
│   │   ├── scrapers/
│   │   │   ├── audio_scraper.py
│   │   │   └── frases_scraper.py
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── pomodoro.py
│   │   └── trees.py
│   ├── tests/
│   │   └── test_api.py
│   ├── main.py
│   ├── requirements.txt
│   └── run.py
└── frontend/
    ├── css/
    │   └── styles.css
    ├── img/
    │   └── forest-logo.png
    ├── js/
    │   ├── api.js
    │   ├── auth.js
    │   ├── inventory.js
    │   └── pomodoro.js
    ├── index.html
    ├── inventory.html
    └── pomodoro.html
```

## Despliegue

Para un despliegue en producción, se recomienda:

1. Subir el código a un repositorio de GitHub.
2. Configurar un servicio como Railway para el despliegue automático.
3. Definir dos servicios en `railway.yaml`: uno para el backend y otro para el frontend.

## Licencia

Este proyecto está disponible como código abierto bajo los términos de la [Licencia MIT](https://opensource.org/licenses/MIT).
