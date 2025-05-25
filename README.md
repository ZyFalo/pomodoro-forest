# Pomodoro Forest 🌲⏱️

Pomodoro Forest es una aplicación web que combina la técnica Pomodoro con sonidos de bosque y frases motivacionales, además de un pequeño "juego" para coleccionar árboles al terminar cada sesión. Cuanto más te concentres, más árboles podrás cultivar en tu bosque virtual.

## Características 🌟

- **Técnica Pomodoro**: Temporizador configurable para gestionar tu tiempo de trabajo.
- **Ambientes sonoros**: Cada sesión incluye sonidos relajantes de bosque.
- **Frases motivacionales**: Frases aleatorias para mantenerte motivado durante tus sesiones.
- **Colección de árboles**: Gana un árbol único por cada sesión completada con diferentes niveles de rareza.
- **Sistema de probabilidad**: Algunos árboles son más raros que otros, basado en su valor de probabilidad.
- **Inventario personal**: Gestiona y visualiza tu bosque virtual.

## Tecnologías 💻

### Backend
- **Python + FastAPI**: API REST con validación y documentación automática.
- **MongoDB Atlas**: Base de datos en la nube para almacenar usuarios y árboles.
- **JWT**: Gestión de sesión de usuario mediante tokens.
- **Web Scraping**: Extracción de sonidos de bosque y frases motivacionales.
- **Sistema de Probabilidades**: Implementación de selección ponderada para árboles según rareza.
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

### Scripts disponibles

- `run.bat`: Inicia el servidor en modo producción
- `dev_server.bat`: Inicia el servidor en modo desarrollo
- `setup_env.bat`: Configura las variables de entorno
- `run_migration.bat`: Ejecuta la migración para corregir la estructura de la base de datos
- `add_probability.bat`: Añade valores de probabilidad a los árboles existentes

### Scripts de migración

El proyecto incluye scripts de migración para manejar cambios en la estructura de la base de datos:

1. **migration_tree_templates.py**: Corrige la estructura de datos para asegurar que:
   - Los árboles template estén en la colección 'trees'
   - Los árboles de usuario estén en el array 'trees' de cada usuario
   - Se eliminen árboles duplicados

2. **add_probability_to_trees.py**: Añade el campo de probabilidad a los árboles template existentes para implementar el sistema de rareza

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

## API Endpoints

### Autenticación
- `POST /api/register`: Registro de nuevo usuario
- `POST /api/token`: Inicio de sesión y generación de token JWT

### Pomodoro
- `POST /api/start-pomodoro`: Inicia una sesión Pomodoro
- `GET /api/motivational-phrase`: Obtiene una frase motivacional aleatoria
- `POST /api/complete-pomodoro`: Marca un pomodoro como completado y otorga un árbol (selección basada en probabilidad)
- `GET /api/tree-types`: Obtiene los tipos de árboles disponibles

### Árboles
- `GET /api/trees`: Obtiene todos los árboles del usuario
- `DELETE /api/trees/{tree_id}`: Elimina un árbol del inventario del usuario
- `PUT /api/trees/{tree_id}`: Actualiza la información de un árbol

### Estadísticas
- `GET /api/user/stats`: Obtiene estadísticas del usuario
- `POST /api/user/stats/update`: Actualiza estadísticas del usuario

### Administración (requiere privilegios)
- `GET /api/admin/tree-templates`: Obtiene plantillas de árboles
- `POST /api/admin/tree-templates`: Crea nueva plantilla de árbol
- `PUT /api/admin/tree-templates/{template_id}`: Actualiza una plantilla existente
- `DELETE /api/admin/tree-templates/{template_id}`: Elimina una plantilla

## Autores 👥

William Andrés Peña Vargas

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
5. ¡Al finalizar, recibirás un árbol único para tu colección basado en un sistema de probabilidades!
6. Visita "Mi Bosque" para ver y gestionar tus árboles ganados.
7. Los árboles más raros tienen menos probabilidad de aparecer, lo que hace más emocionante coleccionarlos todos.

## Sistema de Probabilidad de Árboles

Cada tipo de árbol en Pomodoro Forest tiene un valor de probabilidad asignado que determina su rareza:

- **Árboles comunes**: Mayor probabilidad (15-25)
- **Árboles poco comunes**: Probabilidad media (8-14)
- **Árboles raros**: Baja probabilidad (3-7)
- **Árboles legendarios**: Muy baja probabilidad (1-2)

Cuando completas un pomodoro, el sistema usa un algoritmo de selección ponderada para determinar qué árbol recibes, teniendo en cuenta estos valores de probabilidad.

### Ejemplo:

Si tienes cuatro tipos de árboles con estas probabilidades:
- Pino: 20 (común)
- Roble: 15 (común)
- Cerezo: 10 (poco común)
- Secuoya: 5 (raro)

La probabilidad de obtener cada árbol será:
- Pino: 40%
- Roble: 30%
- Cerezo: 20% 
- Secuoya: 10%

Esto hace que sea emocionante completar pomodoros y coleccionar los árboles más raros.

## Estructura del proyecto

```
proyecto/
├── backend/
│   ├── app/
│   │   ├── scrapers/
│   │   │   ├── audio_scraper.py
│   │   │   ├── frases_cache.json
│   │   │   └── frases_scraper.py
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── pomodoro.py
│   │   ├── stats.py
│   │   ├── tree_templates.py
│   │   └── trees.py
│   ├── tests/
│   │   └── test_api.py
│   ├── add_probability_to_trees.py
│   ├── main.py
│   ├── migration_tree_templates.py
│   ├── railway_fix.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── css/
│   │   └── styles.css
│   ├── img/
│   │   ├── forest-logo.png
│   │   └── forest-logo.svg
│   ├── js/
│   │   ├── animations.js
│   │   ├── api.js
│   │   ├── auth.js
│   │   ├── inventory.js
│   │   └── pomodoro.js
│   ├── index.html
│   ├── inventory.html
│   └── pomodoro.html
├── add_probability.bat
├── dev_server.bat
├── Procfile
├── railway.json
├── README.md
├── requirements.txt
├── run_migration.bat
├── run.bat
├── setup_env.bat
└── setup.bat
```

## Despliegue

Para un despliegue en producción, se recomienda:

1. Subir el código a un repositorio de GitHub.
2. Configurar un servicio como Railway para el despliegue automático.
3. Definir dos servicios en `railway.yaml`: uno para el backend y otro para el frontend.

## Estructura de la Base de Datos

### Colecciones en MongoDB

#### Usuarios

```json
{
  "_id": "ObjectId",
  "username": "string",
  "email": "string",
  "hashed_password": "string",
  "trees": [
    {
      "_id": "string",
      "name": "string",
      "category": "string",
      "description": "string",
      "image_url": "string"
    }
  ],
  "pomodoros_completed": "number",
  "total_focus_minutes": "number",
  "total_trees": "number",
}
```

#### Árboles (Plantillas)

```json
{
  "_id": "ObjectId",
  "name": "string",
  "category": "string",
  "description": "string",
  "image_url": "string",
  "probability": "number",
  "is_template": "boolean",
}
```

## Licencia

Este proyecto está disponible como código abierto bajo los términos de la [Licencia MIT](https://opensource.org/licenses/MIT).
