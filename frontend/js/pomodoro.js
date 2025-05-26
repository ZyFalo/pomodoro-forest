/**
 * Variables para manejar el estado del pomodoro
 */
let pomodoroTimer = null;
let endTime = null;
let audioElement = null;
let isRunning = false;
let phraseInterval = null;

/**
 * Espera a que el DOM esté cargado
 */
document.addEventListener('DOMContentLoaded', () => {
    // Redirige al usuario si no está autenticado
    if (!api.isAuthenticated()) {
        window.location.href = 'index.html';
        return;
    }

    // Inicializa los componentes de la página
    initPomodoro();
});

/**
 * Inicializa el componente Pomodoro
 */
function initPomodoro() {
    // Elementos del DOM
    const startButton = document.getElementById('startButton');
    const stopButton = document.getElementById('stopButton');
    const timerDisplay = document.getElementById('timer');
    const minutesInput = document.getElementById('minutesInput');
    const motivationalPhraseElement = document.getElementById('motivationalPhrase');
    const audioContainer = document.getElementById('audioContainer');
    
    // Inicializa el botón de inicio
    startButton.addEventListener('click', async () => {
        if (isRunning) return;
        
        // Obtiene la duración del input
        const duration = parseInt(minutesInput.value);
        if (isNaN(duration) || duration <= 0) {
            alert('Por favor, ingresa una duración válida.');
            return;
        }
        
        try {
            // Deshabilita botones y muestra carga
            startButton.disabled = true;
            startButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Iniciando...';
            
            // MODIFICACIÓN: En lugar de usar la fecha del servidor, calculamos localmente
            const durationInSeconds = duration * 60;
            endTime = new Date(Date.now() + durationInSeconds * 1000);            // Inicia el pomodoro en el servidor
            const pomodoroData = await api.startPomodoro(duration);
            
            // Muestra la frase motivacional
            motivationalPhraseElement.textContent = pomodoroData.motivational_phrase;
            motivationalPhraseElement.classList.add('fade-in');
            
            // Configura el audio y muestra los controles
            if (audioContainer) {
                audioContainer.classList.remove('d-none');
            }
            setupAudio(pomodoroData.audio_url, audioContainer);
            
            // Cambia el estado de los botones
            startButton.classList.add('d-none');
            stopButton.classList.remove('d-none');
            
            // Oculta el contenedor de configuración y muestra mensaje de sesión activa
            const timerConfigContainer = document.getElementById('timerConfigContainer');
            const activePomodoroMessage = document.getElementById('activePomodoroMessage');
            const activeSessionDuration = document.getElementById('activeSessionDuration');
            
            if (timerConfigContainer) timerConfigContainer.classList.add('d-none');
            if (activePomodoroMessage) {
                if (activeSessionDuration) activeSessionDuration.textContent = duration;
                activePomodoroMessage.classList.remove('d-none');
            }
              // Inicia el temporizador
            isRunning = true;
            updateTimer();
            pomodoroTimer = setInterval(updateTimer, 1000);
            
            // Limpia historial de frases al comenzar un nuevo pomodoro
            frasesMostradas.length = 0;
              
            // Configura el sistema para actualizar frases cada 5 segundos
            // Llamamos primero a updateMotivationalPhrase para obtener la primera frase
            await updateMotivationalPhrase(); // Obtener primera frase inmediatamente
            
            console.log('Sistema de actualización de frases inicializado');
            // Implementamos un mecanismo de actualización más robusto
            const INTERVALO_FRASES = 10000; // 5 segundos
            
            // Limpiamos cualquier temporizador existente primero
            if (phraseInterval) {
                clearTimeout(phraseInterval);
                phraseInterval = null;
            }
            
            // Función para programar la próxima actualización
            function programarProximaActualizacion() {
                console.log('Programando próxima actualización de frase en 5 segundos');
                
                // Solo programar si el pomodoro sigue en ejecución
                if (!isRunning) {
                    console.log('Pomodoro ya no está en ejecución, no se programarán más actualizaciones');
                    return;
                }
                
                // Programar la próxima actualización
                phraseInterval = setTimeout(async () => {
                    console.log('Ejecutando actualización programada de frase');
                    if (isRunning) {
                        await updateMotivationalPhrase();
                        // Programar la siguiente después de completar esta
                        programarProximaActualizacion();
                    }
                }, INTERVALO_FRASES);
            }
            
            // Iniciar el ciclo de actualizaciones
            programarProximaActualizacion();
        } catch (error) {
            console.error('Error al iniciar Pomodoro:', error);
            alert('Error al iniciar el Pomodoro. Por favor, intenta de nuevo.');
            
            // Restaura el botón de inicio
            startButton.disabled = false;
            startButton.innerHTML = '<i class="bi bi-play-fill"></i> Iniciar Pomodoro';
        }
    });
    
    // Inicializa el botón de parada
    stopButton.addEventListener('click', stopPomodoro);
}

/**
 * Actualiza el display del temporizador
 */
function updateTimer() {
    const timerDisplay = document.getElementById('timer');
    const now = new Date();
    
    // Calcula el tiempo restante
    let diff = Math.max(0, Math.round((endTime - now) / 1000));
    
    if (diff <= 0) {
        // El pomodoro ha terminado
        completePomodoro();
        return;
    }
    
    // Calcula minutos y segundos
    const minutes = Math.floor(diff / 60);
    const seconds = diff % 60;
    
    // Actualiza el display con formato MM:SS
    timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

/**
 * Configura el elemento de audio
 */
function setupAudio(audioUrl, container) {
    // Crea un nuevo elemento de audio
    audioElement = document.createElement('audio');
    audioElement.controls = true;
    audioElement.autoplay = true;
    audioElement.loop = true; // Configurar reproducción en bucle
    
    // Configurar volumen inicial al 50%
    audioElement.volume = 0.5;
    
    // Crea una fuente para el audio
    const source = document.createElement('source');
    source.src = audioUrl;
    source.type = 'audio/mpeg';
    
    // Agrega la fuente al elemento de audio
    audioElement.appendChild(source);
    
    // Crea un contenedor para controles adicionales
    const audioControls = document.createElement('div');
    audioControls.className = 'audio-controls mt-3';
    
    // Agrega control de volumen
    const volumeControl = document.createElement('div');
    volumeControl.className = 'volume-control d-flex align-items-center mt-2';
    volumeControl.innerHTML = `
        <i class="bi bi-volume-down me-2 text-white"></i>
        <input type="range" class="form-range" min="0" max="1" step="0.1" value="0.5" id="volumeControl">
        <i class="bi bi-volume-up ms-2 text-white"></i>
    `;
    
    // Agrega los controles al contenedor
    audioControls.appendChild(volumeControl);
    
    // Limpia el contenedor y agrega el elemento de audio y controles
    container.innerHTML = '';
    container.appendChild(audioElement);
    container.appendChild(audioControls);
    
    // Configura el evento para el control de volumen
    document.getElementById('volumeControl').addEventListener('input', function(e) {
        audioElement.volume = e.target.value;
    });
}

/**
 * Mantiene un historial de frases mostradas para evitar repeticiones inmediatas
 */
const frasesMostradas = [];
const MAX_FRASES_HISTORIAL = 5; // Número máximo de frases para recordar

/**
 * Actualiza la frase motivacional
 */
async function updateMotivationalPhrase() {
    if (!isRunning) {
        console.log('No se actualiza la frase porque el pomodoro no está en ejecución');
        return;
    }
    
    console.log('Iniciando actualización de frase motivacional...');
    
    try {
        const phraseData = await api.getMotivationalPhrase();
        const motivationalPhraseElement = document.getElementById('motivationalPhrase');
        
        if (!motivationalPhraseElement || !phraseData || !phraseData.phrase) {
            console.error('Error: No se pudo actualizar la frase motivacional - Elemento o datos no disponibles');
            return;
        }
        
        console.log('Obtenida nueva frase motivacional:', phraseData.phrase);
        
        // Si la frase es la misma que alguna reciente, intentamos hasta 3 veces obtener una diferente
        if (frasesMostradas.includes(phraseData.phrase)) {
            console.log('Frase repetida, solicitando otra... (frases mostradas anteriormente:', frasesMostradas, ')');
            // Incrementar contador de intentos (en variable global o como atributo)
            window.phraseRetryCount = (window.phraseRetryCount || 0) + 1;
            
            if (window.phraseRetryCount < 3) {
                // Esperar un poco y volver a intentar con una solicitud nueva
                console.log(`Intento ${window.phraseRetryCount} de 3: Solicitando frase diferente en 800ms`);
                setTimeout(updateMotivationalPhrase, 800);
                return;
            } else {
                // Después de 3 intentos, añadimos un marcador visual aleatorio
                console.log('Después de 3 intentos, añadiendo emoji a la frase repetida');
                const emojis = ['✨', '🌟', '💫', '⚡', '🔥', '🌈', '🌻', '🌱', '🌲', '🍃'];
                const randomEmoji = emojis[Math.floor(Math.random() * emojis.length)];
                phraseData.phrase = `${randomEmoji} ${phraseData.phrase}`;
                window.phraseRetryCount = 0;
            }
        } else {
            // Reiniciar contador si la frase es diferente
            window.phraseRetryCount = 0;
        }
        
        // Actualizar historial de frases mostradas
        frasesMostradas.push(phraseData.phrase);
        if (frasesMostradas.length > MAX_FRASES_HISTORIAL) {
            frasesMostradas.shift(); // Elimina la frase más antigua
        }
        
        console.log('Historial actual de frases:', frasesMostradas);
          
        // Añade animación para la transición de salida
        console.log('Iniciando animación de transición de frase');
        motivationalPhraseElement.classList.remove('phrase-fade-in');
        motivationalPhraseElement.classList.add('phrase-fade-out');
        
        // Esperar a que termine la animación de salida antes de cambiar el texto
        setTimeout(() => {
            if (!isRunning) return; // Verificar nuevamente por si se detuvo durante la animación
            
            // Actualizar el texto
            console.log('Actualizando texto de la frase a:', phraseData.phrase);
            motivationalPhraseElement.textContent = phraseData.phrase;
            
            // Quitar la animación de salida y reiniciar
            motivationalPhraseElement.classList.remove('phrase-fade-out');
            
            // Forzar un reflow para asegurar que la animación se reinicie correctamente
            void motivationalPhraseElement.offsetWidth;
            
            // Aplicar animación de entrada
            motivationalPhraseElement.classList.add('phrase-fade-in');
            console.log('Animación de entrada aplicada');
        }, 500); // 500ms, corresponde a la duración de la animación de salida
        
        console.log('Frase actualizada correctamente:', phraseData.phrase);
    } catch (error) {
        console.error('Error al obtener frase motivacional:', error);
        
        // En caso de error, intentar nuevamente después de un breve retraso
        console.log('Programando reintento en 2 segundos debido a error');
        setTimeout(updateMotivationalPhrase, 2000);
    }
}

/**
 * Detiene el pomodoro actual
 */
function stopPomodoro() {
    console.log('Deteniendo el pomodoro y limpiando todos los temporizadores');
    
    // Limpia los intervalos
    if (pomodoroTimer) {
        clearInterval(pomodoroTimer);
        pomodoroTimer = null;
    }
    
    // Corregimos para usar clearTimeout ya que phraseInterval es un setTimeout
    if (phraseInterval) {
        clearTimeout(phraseInterval);
        phraseInterval = null;
        console.log('Se ha detenido el temporizador de actualización de frases');
    }
    
    // Detiene el audio
    if (audioElement) {
        audioElement.pause();
        audioElement.currentTime = 0;
    }
    
    // Restaura la interfaz
    const startButton = document.getElementById('startButton');
    const stopButton = document.getElementById('stopButton');
    
    startButton.disabled = false;
    startButton.innerHTML = '<i class="bi bi-play-fill"></i> Iniciar Pomodoro';
    startButton.classList.remove('d-none');
    stopButton.classList.add('d-none');
    
    // Vuelve a mostrar el contenedor de configuración y oculta el mensaje de sesión activa
    const timerConfigContainer = document.getElementById('timerConfigContainer');
    const activePomodoroMessage = document.getElementById('activePomodoroMessage');
    
    if (timerConfigContainer) timerConfigContainer.classList.remove('d-none');
    if (activePomodoroMessage) activePomodoroMessage.classList.add('d-none');
    
    // Restaura el mensaje del contenedor de audio
    const audioContainer = document.getElementById('audioContainer');
    if (audioContainer) {
        audioContainer.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="audio-icon me-3">
                    <i class="bi bi-music-note-beamed"></i>
                </div>
                <p class="mb-0 text-white">El audio ambiental del bosque se reproducirá en bucle al iniciar el Pomodoro.</p>
            </div>
        `;
    }
    
    // Restaura el temporizador
    const timerDisplay = document.getElementById('timer');
    const minutesInput = document.getElementById('minutesInput');
    const minutes = minutesInput ? minutesInput.value : '25';
    timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:00`;
    
    // Cambia el estado
    isRunning = false;
}

/**
 * Marca el pomodoro como completado
 */
async function completePomodoro() {
    // Detiene el temporizador
    stopPomodoro();
    
    try {
        // Obtener la duración del pomodoro que se acaba de completar
        const duration = parseInt(document.getElementById('minutesInput').value || '25');
        
        // Mostrar mensaje de carga
        console.log('Notificando al servidor sobre el pomodoro completado...');
        
        // Mostrar notificación de carga
        const loadingToast = showToast('Guardando tu progreso...', 'info', false);
        
        try {            // Primero, completar el pomodoro - Esto incrementará el contador en el servidor
            console.log('Completando pomodoro...');
            const result = await api.completePomodoro();
            console.log('Resultado de completar pomodoro:', result);
            
            // Ocultar la notificación de carga
            hideToast(loadingToast);
            
            if (!result || !result.tree) {
                throw new Error('No se recibió un árbol del servidor');
            }
            
            // Ahora que se completó el pomodoro, obtener las estadísticas actualizadas
            // que ya tendrán el contador de pomodoros_completed incrementado
            console.log('Obteniendo estadísticas actualizadas después de completar pomodoro...');
            const updatedStats = await api.getUserStats();
            
            // Actualizar los minutos de enfoque (no se incrementan automáticamente en el backend)
            updatedStats.total_focus_minutes += duration;
            
            // Actualizar estadísticas en la base de datos con los minutos actualizados
            // El contador de pomodoros ya fue incrementado por el backend en completePomodoro
            console.log('Actualizando total de minutos en estadísticas del usuario...');
            await api.updateUserStats({
                pomodoros_completed: updatedStats.pomodoros_completed,
                total_focus_minutes: updatedStats.total_focus_minutes
            });
            
            // Actualizar también las estadísticas localmente
            localStorage.setItem('pomodoros_completed', updatedStats.pomodoros_completed.toString());
            localStorage.setItem('total_focus_minutes', updatedStats.total_focus_minutes.toString());
            localStorage.setItem('total_trees', updatedStats.total_trees.toString()); // Ya incluye el nuevo árbol
            
            // Actualizar las estadísticas en el DOM si existen los elementos
            const pomodorosCompletedValue = document.getElementById('pomodorosCompletedValue');
            const focusMinutesValue = document.getElementById('focusMinutesValue');
            
            if (pomodorosCompletedValue) pomodorosCompletedValue.textContent = userStats.pomodoros_completed;
            if (focusMinutesValue) focusMinutesValue.textContent = userStats.total_focus_minutes;
            
            // Finalmente - Mostrar el árbol ganado
            console.log('Mostrando árbol ganado:', result.tree);
            showEarnedTree(result.tree);
        } catch (error) {
            // Ocultar la notificación de carga si todavía está visible
            hideToast(loadingToast);
            throw error;
        }
    } catch (error) {
        console.error('Error al completar Pomodoro:', error);
        
        // Mostrar un toast de error más amigable
        showToast(
            'No pudimos guardar tu árbol en este momento, pero tu progreso local está guardado. Por favor, intenta de nuevo más tarde.', 
            'error',
            true
        );
        
        // Si hay un error, intentar actualizar solo las estadísticas locales
        try {
            // Obtener estadísticas actuales antes de intentar actualizarlas
            const stats = await api.getUserStats();
            await api.updateUserStats(stats);
        } catch (e) {
            console.log('No se pudieron actualizar las estadísticas en el servidor:', e);
        }
    }
}

// Helper para mostrar notificaciones tipo toast
function showToast(message, type = 'info', autoHide = true) {
    // Crear contenedor de toasts si no existe
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Crear el toast
    const toastId = 'toast-' + Date.now();
    const toastEl = document.createElement('div');
    toastEl.className = `toast show bg-${type === 'error' ? 'danger' : type} text-white`;
    toastEl.id = toastId;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    const icon = type === 'info' ? 'info-circle' : 
                type === 'error' ? 'exclamation-triangle' :
                type === 'success' ? 'check-circle' : 'bell';
                
    toastEl.innerHTML = `
        <div class="toast-header bg-${type === 'error' ? 'danger' : type} text-white">
            <i class="bi bi-${icon} me-2"></i>
            <strong class="me-auto">Pomodoro Forest</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    toastContainer.appendChild(toastEl);
    
    // Auto-ocultar después de 5 segundos si se solicita
    if (autoHide) {
        setTimeout(() => {
            hideToast(toastId);
        }, 5000);
    }
    
    return toastId;
}

function hideToast(toastId) {
    const toast = typeof toastId === 'string' ? document.getElementById(toastId) : toastId;
    if (toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 500);
    }
}

/**
 * Muestra el árbol ganado en un modal
 */
function showEarnedTree(tree) {
    // Usar el modal existente en pomodoro.html
    const modal = document.getElementById('treeEarnedModal');
    
    if (!modal) {
        console.error('Error: Modal #treeEarnedModal no encontrado en el DOM');
        return;
    }
    
    // Actualizar contenido del modal con la información del árbol
    document.getElementById('earnedTreeImage').src = tree.image_url;
    document.getElementById('earnedTreeName').textContent = tree.name;
    document.getElementById('earnedTreeDescription').textContent = tree.description;
    
    // Actualizar la categoría si existe el elemento
    const categoryElement = document.getElementById('earnedTreeCategory');
    if (categoryElement && tree.category) {
        categoryElement.textContent = tree.category;
    }
    
    // Asegurarse que el modal tiene la clase necesaria para Bootstrap
    if (!modal.classList.contains('modal')) {
        modal.classList.add('modal', 'fade');
    }
    
    // Crear una instancia del modal de Bootstrap y mostrarlo
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Activar la animación de confeti cuando se muestre el modal
    modal.addEventListener('shown.bs.modal', function() {
        animateConfetti();
    }, { once: true }); // El evento se dispara solo una vez
}

/**
 * Efecto de confeti para celebrar
 */
function animateConfetti() {
    const confettis = document.querySelectorAll('.confetti');
    confettis.forEach((confetti, index) => {
        const delay = index * 100;
        const duration = 1000 + Math.random() * 1000;
        const x = Math.random() * 300 - 150;
        const y = Math.random() * 200 - 100;
        const rotation = Math.random() * 360;
        
        confetti.style.backgroundColor = getRandomColor();
        confetti.style.animation = `fall ${duration}ms ease-in ${delay}ms forwards`;
        confetti.style.transform = `translate(${x}px, ${y}px) rotate(${rotation}deg)`;
        confetti.style.opacity = '1';
    });
}

/**
 * Genera un color aleatorio para el confeti
 */
function getRandomColor() {
    const colors = [
        '#FF6B6B', '#4ECDC4', '#FFC857', '#77DD77', '#FDFD96', 
        '#84B1ED', '#FFCC5C', '#FF85A2', '#63C5DA'
    ];
    return colors[Math.floor(Math.random() * colors.length)];
}
