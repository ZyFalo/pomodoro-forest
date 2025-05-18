/**
 * Configuración del API
 */
const API_URL = 'http://localhost:8000';

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
    },

    /**
     * Realiza una petición a la API
     */
    async fetchAPI(endpoint, options = {}) {
        const API_URL = 'http://localhost:8000';
        
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
        
        try {
            const response = await fetch(`${API_URL}${endpoint}`, fetchOptions);
            
            // Si la respuesta no es exitosa, lanzar error
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
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
    },

    /**
     * Función para registrar un nuevo usuario
     */
    async register(username, password, email = '') {
        return this.fetchAPI('/register', {
            method: 'POST',
            body: JSON.stringify({ username, password, email })
        });
    },

    /**
     * Función para iniciar sesión
     */
    async login(username, password) {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error al iniciar sesión');
        }

        return await response.json();
    },

    /**
     * Función para iniciar un pomodoro
     */
    async startPomodoro(duration = 25) {
        return this.fetchAPI('/start-pomodoro', {
            method: 'POST',
            body: JSON.stringify({ duration })
        });
    },

    /**
     * Función para obtener una frase motivacional
     */
    async getMotivationalPhrase() {
        return this.fetchAPI('/motivational-phrase');
    },

    /**
     * Función para marcar un pomodoro como completado
     */
    async completePomodoro() {
        return this.fetchAPI('/complete-pomodoro', {
            method: 'POST'
        });
    },

    /**
     * Función para obtener la lista de árboles del usuario
     */
    async getTrees() {
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
    },

    /**
     * Función para eliminar un árbol
     */
    async deleteTree(treeId) {
        return this.fetchAPI(`/trees/${treeId}`, {
            method: 'DELETE'
        });
    },    /**
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
            };
            
            // Realizar la solicitud PUT
            const response = await this.fetchAPI(`/trees/${treeId}`, {
                method: 'PUT',
                body: JSON.stringify(treeData)
            });
            
            console.log("Respuesta de actualización:", response);
            return response;
        } catch (error) {
            console.error("Error al actualizar árbol:", error);
            throw error;
        }
    },/**
     * Función para obtener estadísticas del usuario
     */
    async getUserStats() {
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
    },

    /**
     * Función para actualizar las estadísticas del usuario
     */
    async updateUserStats(stats) {
        try {
            return await this.fetchAPI('/user/stats/update', {
                method: 'POST',
                body: JSON.stringify(stats)
            });
        } catch (error) {
            console.error("Error actualizando estadísticas:", error);
            throw error;
        }
    },    /**
     * Función para obtener información del usuario actual
     */
    async getCurrentUser() {
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
    }
};
