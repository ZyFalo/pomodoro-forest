/**
 * Configuración del API
 */
// Detectar si estamos en producción o desarrollo
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';

// Base URL para las API
// En producción se usa una ruta relativa, en desarrollo se usa la URL completa
const API_BASE_URL = isProduction ? '/api' : 'http://localhost:8000';

// Función auxiliar para construir rutas correctamente
function buildApiPath(endpoint) {
    // Elimina barras diagonales iniciales si existen
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;
    
    // En desarrollo, añade /api/ al inicio ya que la URL base no lo incluye
    // En producción, la URL base ya incluye /api/
    if (!isProduction) {
        return `${API_BASE_URL}/api/${cleanEndpoint}`;
    }
    
    // En producción, simplemente concatena
    return `${API_BASE_URL}/${cleanEndpoint}`;
}

/**
 * Funciones para manejar las peticiones HTTP al API
 */
const api = {
    /**
     * Obtiene el token JWT del localStorage
     */
    getToken() {
        return localStorage.getItem('token');
    },

    /**
     * Verifica si el usuario está autenticado
     */
    isAuthenticated() {
        return !!this.getToken();
    },

    /**
     * Realiza logout eliminando el token
     */
    logout() {
        localStorage.removeItem('token');
        window.location.href = 'index.html';
    },    /**
     * Realiza una petición a la API
     */    async fetchAPI(endpoint, options = {}) {
        // Configuración por defecto
        const fetchOptions = {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        // Añadir token de autenticación si existe
        const token = localStorage.getItem('token');
        if (token) {
            fetchOptions.headers['Authorization'] = `Bearer ${token}`;
        }
        
        const url = buildApiPath(endpoint);
        console.log(`Realizando petición a: ${url}`);
        
        try {
            const response = await fetch(url, fetchOptions);
            
            // Si la respuesta no es exitosa, intentar obtener más detalles del error
            if (!response.ok) {
                let errorMessage;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || `Error ${response.status}: ${response.statusText}`;
                } catch (e) {
                    // Si no se puede analizar el JSON, usar el texto del error
                    const errorText = await response.text().catch(() => '');
                    errorMessage = errorText || `Error ${response.status}: ${response.statusText}`;
                }
                
                // Registro detallado del error para depuración
                console.error(`Error en la petición a ${endpoint}:`, {
                    statusCode: response.status,
                    statusText: response.statusText,
                    message: errorMessage,
                    endpoint: endpoint,
                    method: fetchOptions.method
                });
                
                throw new Error(errorMessage);
            }
            
            // Si la respuesta está vacía, devolver un objeto vacío
            if (response.status === 204) {
                return {};
            }
            
            // Devolver los datos como JSON
            return await response.json();
        } catch (error) {
            console.error(`Error en fetchAPI (${endpoint}):`, error);
            throw error;
        }
    },    /**
     * Función para registrar un nuevo usuario
     */    async register(username, password, email = '') {
        return this.fetchAPI('/register', {
            method: 'POST',
            body: JSON.stringify({ username, password, email })
        });
    },/**
     * Función para iniciar sesión
     */async login(username, password) {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        try {
            // Usar nuestro método fetchAPI pero con un formato diferente para el cuerpo
            // Corregimos la ruta para evitar la duplicación del prefijo /api
            const response = await fetch(buildApiPath('/token'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });
            
            // Manejar errores
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Almacenar el token y el nombre de usuario directamente aquí
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('username', username);
            
            return data;
        } catch (error) {
            console.error('Error durante el login:', error);
            throw error;
        }
    },    /**
     * Función para iniciar un pomodoro
     */    async startPomodoro(duration = 25) {
        return this.fetchAPI('/start-pomodoro', {
            method: 'POST',
            body: JSON.stringify({ duration })
        });
    },    /**
     * Función para obtener una frase motivacional
     */    async getMotivationalPhrase() {
        return this.fetchAPI('/motivational-phrase');
    },    /**
     * Función para marcar un pomodoro como completado
     */    async completePomodoro() {
        return this.retryOnServerError(async () => {
            return await this.fetchAPI('/complete-pomodoro', {
                method: 'POST'
            });
        }, 3, 1500); // 3 reintentos con 1.5 segundos de espera inicial
    },    /**
     * Función para obtener la lista de árboles del usuario
     */async getTrees() {
        try {
            const response = await this.fetchAPI('/trees');
            console.log("Respuesta de API trees:", response);
            
            // Verifica si la respuesta contiene un arreglo directamente o dentro de un objeto
            if (Array.isArray(response)) {
                return response;
            } else if (response && Array.isArray(response.trees)) {
                return response.trees;
            }
            
            // Si no se encontró un arreglo, devuelve un arreglo vacío
            console.warn("Formato de respuesta inesperado, se devuelve array vacío");
            return [];
        } catch (error) {
            console.error("Error en getTrees:", error);
            return []; // Devuelve un array vacío en caso de error
        }
    },    /**
     * Función para eliminar un árbol
     */    async deleteTree(treeId) {
        console.log(`API: Eliminando árbol con ID: ${treeId}`);
        
        if (!treeId) {
            throw new Error('ID de árbol no proporcionado');
        }
        
        return this.retryOnServerError(async () => {
            return await this.fetchAPI(`/trees/${treeId}`, {
                method: 'DELETE'
            });
        }, 2, 1000); // 2 reintentos con 1 segundo de espera inicial
    },
    /**
     * Función para actualizar un árbol
     */
    async updateTree(treeId, tree) {
        console.log(`Actualizando árbol ${treeId} con:`, tree);
        try {
            // Asegurarse de que los datos son correctos
            const treeData = {
                name: tree.name || '',
                category: tree.category || '',
                image_url: tree.image_url || '',
                description: tree.description || ''
            };            // Realizar la solicitud PUT
            const response = await this.fetchAPI(`/trees/${treeId}`, {
                method: 'PUT',
                body: JSON.stringify(treeData)
            });
            
            console.log("Respuesta de actualización:", response);
            return response;
        } catch (error) {
            console.error("Error al actualizar árbol:", error);
            throw error;
        }    },/**
     * Función para obtener estadísticas del usuario
     */    async getUserStats() {
        try {
            // Intenta obtener datos del servidor
            const data = await this.fetchAPI('/user/stats');
            console.log("Estadísticas recibidas del servidor:", data);
            
            // Verificar que la respuesta contiene los campos esperados
            if (data) {
                // Guarda las estadísticas en localStorage para uso futuro, con valores por defecto si no existen
                localStorage.setItem('pomodoros_completed', (data.pomodoros_completed || 0).toString());
                localStorage.setItem('total_focus_minutes', (data.total_focus_minutes || 0).toString());
                localStorage.setItem('total_trees', (data.total_trees || 0).toString());
                
                return {
                    total_trees: data.total_trees || 0,
                    pomodoros_completed: data.pomodoros_completed || 0,
                    total_focus_minutes: data.total_focus_minutes || 0
                };
            } else {
                throw new Error("Respuesta vacía del servidor");
            }
        } catch (error) {
            console.warn("No se pudieron obtener estadísticas del servidor, usando datos locales:", error);
            
            // Devolver valores almacenados localmente o valores por defecto
            return {
                total_trees: parseInt(localStorage.getItem('total_trees') || "0"),
                pomodoros_completed: parseInt(localStorage.getItem('pomodoros_completed') || "0"),
                total_focus_minutes: parseInt(localStorage.getItem('total_focus_minutes') || "0")
            };
        }
    },    /**
     * Función para actualizar las estadísticas del usuario
     */    async updateUserStats(stats) {
        try {
            return await this.fetchAPI('/user/stats/update', {
                method: 'POST',
                body: JSON.stringify(stats)
            });
        } catch (error) {
            console.error("Error actualizando estadísticas:", error);
            throw error;
        }
    },
    
    /**
     * Función para obtener los tipos de árboles disponibles
     */    async getTreeTypes() {
        try {
            return await this.fetchAPI('/tree-types');
        } catch (error) {
            console.error("Error al obtener tipos de árboles:", error);
            return []; // En caso de error, devuelve un array vacío
        }
    },/**
     * Función para obtener información del usuario actual
     */    async getCurrentUser() {
        try {
            // Intentar obtener información del usuario del backend
            const data = await this.fetchAPI('/users/me');
            return data;
        } catch (error) {
            console.error("Error obteniendo información del usuario:", error);
            // Si hay error, devolver un objeto con el username almacenado localmente
            return {
                username: localStorage.getItem('username') || "Usuario"
            };
        }
    },
    /**
     * Función para realizar un reintento de una operación API en caso de error del servidor
     * @param {Function} apiCall - Función que realiza la llamada a la API
     * @param {number} maxRetries - Número máximo de reintentos
     * @param {number} delay - Retraso en ms entre reintentos
     */
    async retryOnServerError(apiCall, maxRetries = 2, delay = 1000) {
        let lastError;
        for (let retry = 0; retry <= maxRetries; retry++) {
            try {
                // Si no es el primer intento, mostrar mensaje de reintento
                if (retry > 0) {
                    console.log(`Reintentando operación (${retry}/${maxRetries})...`);
                }
                
                // Intentar realizar la llamada a la API
                return await apiCall();
            } catch (error) {
                lastError = error;
                
                // Solo reintentar en caso de errores del servidor (500+)
                const isServerError = error.message && error.message.includes("500");
                if (!isServerError) {
                    throw error;
                }
                
                if (retry < maxRetries) {
                    console.log(`Error del servidor. Reintentando en ${delay}ms...`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                    // Incrementar el retraso para cada reintento
                    delay *= 1.5;
                }
            }
        }
        
        // Si llegamos aquí, todos los reintentos fallaron
        throw lastError;
    },
};
