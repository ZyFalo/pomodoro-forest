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
    });    // Formulario de Registro
    const registerForm = document.getElementById('registerForm');
    const registerError = document.getElementById('registerError');
    const registerButton = registerForm.querySelector('button[type="submit"]');
    const originalButtonText = registerButton.innerHTML;

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        try {
            registerError.classList.add('d-none');
            
            // Cambiar el botón a estado de carga
            registerButton.disabled = true;
            registerButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Registrando...';
            
            // Validaciones adicionales
            if (username.length < 3) {
                throw new Error('El nombre de usuario debe tener al menos 3 caracteres');
            }
            
            if (password.length < 6) {
                throw new Error('La contraseña debe tener al menos 6 caracteres');
            }
            
            // Valida que las contraseñas coincidan
            if (password !== confirmPassword) {
                throw new Error('Las contraseñas no coinciden');
            }// Intenta registrar al usuario
            const data = await api.register(username, password, email);
            
            // Muestra un mensaje de éxito pero permanece en la misma pestaña
            registerForm.reset();
            
            // Crear un mensaje de éxito
            const successMessage = document.createElement('div');
            successMessage.className = 'alert alert-success';
            successMessage.innerHTML = '<i class="bi bi-check-circle-fill me-2"></i>Registro exitoso. Ya puedes iniciar sesión con tus credenciales en la pestaña "Iniciar sesión".';
            
            // Insertar el mensaje antes del formulario
            registerForm.parentNode.insertBefore(successMessage, registerForm);
            
            // Eliminar el mensaje después de 5 segundos
            setTimeout(() => {
                if (successMessage.parentNode) {
                    // Añadir clase de desvanecimiento
                    successMessage.classList.add('fade');
                    
                    // Eliminar el elemento después de la animación
                    setTimeout(() => {
                        if (successMessage.parentNode) {
                            successMessage.parentNode.removeChild(successMessage);
                        }
                    }, 500);
                }
            }, 5000);        } catch (error) {
            // Muestra el error
            registerError.textContent = error.message;
            registerError.classList.remove('d-none');
        } finally {
            // Restaurar el botón a su estado original
            registerButton.disabled = false;
            registerButton.innerHTML = originalButtonText;
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
