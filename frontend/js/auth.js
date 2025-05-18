/**
 * Espera a que el DOM esté cargado
 */
document.addEventListener('DOMContentLoaded', () => {
    // Verifica si el usuario ya está autenticado
    if (api.isAuthenticated() && window.location.pathname.includes('index.html')) {
        // Redirige al usuario a la página de pomodoro si ya tiene sesión
        window.location.href = 'pomodoro.html';
        return;
    }

    // Inicializa los formularios si estamos en la página de login/registro
    if (document.getElementById('loginForm')) {
        initAuthForms();
    }
});

/**
 * Inicializa los formularios de autenticación
 */
function initAuthForms() {
    // Formulario de Login
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        
        try {
            loginError.classList.add('d-none');
            
            // Intenta hacer login
            const data = await api.login(username, password);
            
            // Guarda el token en localStorage
            localStorage.setItem('token', data.access_token);
            
            // Guarda explícitamente el nombre de usuario
            localStorage.setItem('username', username);
            console.log("Usuario guardado en localStorage:", username);
            
            // Redirige a la página de pomodoro
            window.location.href = 'pomodoro.html';
        } catch (error) {
            // Muestra el error
            loginError.textContent = error.message;
            loginError.classList.remove('d-none');
        }
    });

    // Formulario de Registro
    const registerForm = document.getElementById('registerForm');
    const registerError = document.getElementById('registerError');

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        try {
            registerError.classList.add('d-none');
            
            // Valida que las contraseñas coincidan
            if (password !== confirmPassword) {
                throw new Error('Las contraseñas no coinciden');
            }
              // Intenta registrar al usuario
            const data = await api.register(username, password, email);
            
            // Muestra un mensaje de éxito y cambia a la pestaña de login
            registerForm.reset();
            
            // Crear un mensaje de éxito
            const successMessage = document.createElement('div');
            successMessage.className = 'alert alert-success';
            successMessage.innerHTML = '<i class="bi bi-check-circle-fill me-2"></i>Registro exitoso. Ahora puedes iniciar sesión con tus credenciales.';
            
            // Insertar el mensaje antes del formulario
            registerForm.parentNode.insertBefore(successMessage, registerForm);
            
            // Cambiar a la pestaña de login después de 1 segundo
            setTimeout(() => {
                // Activar la pestaña de login
                document.getElementById('login-tab').click();
                
                // Remover el mensaje de éxito después de cambiar de pestaña
                setTimeout(() => {
                    if (successMessage.parentNode) {
                        successMessage.parentNode.removeChild(successMessage);
                    }
                }, 500);
            }, 1500);
        } catch (error) {
            // Muestra el error
            registerError.textContent = error.message;
            registerError.classList.remove('d-none');
        }
    });
}

/**
 * Función para cerrar sesión
 */
function logout() {
    // Limpiar el token
    localStorage.removeItem('token');
    
    // Limpiar estadísticas 
    localStorage.removeItem('pomodoros_completed');
    localStorage.removeItem('total_focus_minutes');
    localStorage.removeItem('total_trees');
    
    // Mantener el nombre de usuario para depuración
    api.logout();
    
    // Redirigir al login
    window.location.href = 'index.html';
}

/**
 * Función para iniciar sesión
 */
async function login(username, password) {
    try {
        const response = await api.login(username, password);
        
        // Guardar el token y el nombre de usuario explícitamente
        localStorage.setItem('token', response.access_token);
        localStorage.setItem('username', username); // Guardar el username para mostrarlo
        console.log("Usuario guardado:", username); // Debug
        
        return true;
    } catch (error) {
        console.error('Error en login:', error);
        throw error;
    }
}

/**
 * Función para mostrar el nombre de usuario en la navbar
 */
function updateNavbarUsername() {
    const usernameElement = document.getElementById('navbarUsername');
    if (usernameElement) {
        const username = localStorage.getItem('username');
        console.log("Nombre recuperado:", username); // Debug
        
        // Si hay un nombre de usuario, mostrarlo
        if (username) {
            usernameElement.textContent = username;
        } else {
            usernameElement.textContent = "Usuario";
        }
    }
}

// Añade esto al final del archivo auth.js

document.addEventListener('DOMContentLoaded', function() {
    updateNavbarUsername();
    
    // Animación para los campos de formulario con pequeño retraso para asegurar que CSS se aplica primero
    setTimeout(() => {
        document.querySelectorAll('.form-floating').forEach((field, index) => {
            setTimeout(() => {
                field.style.transition = 'all 0.5s ease';
                field.style.opacity = 1;
                field.style.transform = 'translateY(0)';
            }, 100 + (index * 150)); // Ligeramente más rápido
        });
    }, 50); // Pequeño retraso inicial
    
    // Efectos para los botones de tabs
    const tabs = document.querySelectorAll('#authTabs .nav-link');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Resetea la animación de los campos al cambiar de tab
            const targetTabId = this.getAttribute('data-bs-target').substring(1);
            const targetFields = document.querySelector(`#${targetTabId}`).querySelectorAll('.form-floating');
            
            targetFields.forEach((field, index) => {
                field.style.opacity = 0;
                field.style.transform = 'translateY(10px)';
                
                setTimeout(() => {
                    field.style.transition = 'all 0.4s ease';
                    field.style.opacity = 1;
                    field.style.transform = 'translateY(0)';
                }, 150 + (index * 100));
            });
        });
    });
});
