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
            
            // Configura el intervalo para actualizar frases cada 5 minutos
            phraseInterval = setInterval(updateMotivationalPhrase, 5 * 60 * 1000);
        } catch (error) {
            console.error('Error al iniciar Pomodoro:', error);
            alert('Error al iniciar el Pomodoro. Por favor, intenta de nuevo.');
            
            // Restaura el botón de inicio
            startButton.disabled = false;
            startButton.innerHTML = 'Iniciar';
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
 * Actualiza la frase motivacional
 */
async function updateMotivationalPhrase() {
    if (!isRunning) return;
    
    try {
        const phraseData = await api.getMotivationalPhrase();
        const motivationalPhraseElement = document.getElementById('motivationalPhrase');
        
        // Añade animación para la transición
        motivationalPhraseElement.classList.remove('fade-in');
        
        // Pequeño truco para reiniciar la animación
        void motivationalPhraseElement.offsetWidth;
        
        // Actualiza el texto y agrega la animación
        motivationalPhraseElement.textContent = phraseData.phrase;
        motivationalPhraseElement.classList.add('fade-in');
    } catch (error) {
        console.error('Error al obtener frase motivacional:', error);
    }
}

/**
 * Detiene el pomodoro actual
 */
function stopPomodoro() {
    // Limpia los intervalos
    clearInterval(pomodoroTimer);
    clearInterval(phraseInterval);
    
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
        
        // Actualizar estadísticas localmente
        const currentPomodoros = parseInt(localStorage.getItem('pomodoros_completed') || '0');
        const newPomodoros = currentPomodoros + 1;
        localStorage.setItem('pomodoros_completed', newPomodoros.toString());
        
        const currentMinutes = parseInt(localStorage.getItem('total_focus_minutes') || '0');
        const newMinutes = currentMinutes + duration;
        localStorage.setItem('total_focus_minutes', newMinutes.toString());
        
        // Actualizar las estadísticas en el DOM si existe el elemento
        const pomodorosCompletedValue = document.getElementById('pomodorosCompletedValue');
        const focusMinutesValue = document.getElementById('focusMinutesValue');
        
        if (pomodorosCompletedValue) pomodorosCompletedValue.textContent = newPomodoros;
        if (focusMinutesValue) focusMinutesValue.textContent = newMinutes;
        
        // Mostrar mensaje de carga
        console.log('Notificando al servidor sobre el pomodoro completado...');
        
        // Primero - Notificar al servidor que se completó el pomodoro y obtener el árbol
        const result = await api.completePomodoro();
        console.log('Resultado de completar pomodoro:', result);
        
        if (!result || !result.tree) {
            throw new Error('No se recibió un árbol del servidor');
        }
        
        // Segundo - Actualizar estadísticas en la base de datos
        console.log('Actualizando estadísticas del usuario...');
        await api.updateUserStats({
            pomodoros_completed: newPomodoros,
            total_focus_minutes: newMinutes
        });
        
        // Finalmente - Mostrar el árbol ganado
        console.log('Mostrando árbol ganado:', result.tree);
        showEarnedTree(result.tree);
    } catch (error) {
        console.error('Error al completar Pomodoro:', error);
        alert('Error al completar el Pomodoro: ' + (error.message || 'Error desconocido'));
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
