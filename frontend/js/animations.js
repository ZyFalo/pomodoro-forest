/**
 * Archivo para manejar animaciones y mejoras visuales
 */
document.addEventListener('DOMContentLoaded', function() {
    // Añadir clases de animación a los elementos cuando la página carga
    document.querySelectorAll('.card').forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in-up');
        }, 100 * index);
    });
    
    // Animación para tarjetas de árboles en inventario
    if (document.getElementById('inventory')) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        // Añadir observer cuando se carguen los árboles
        const originalLoadInventory = window.loadInventory;
        if (originalLoadInventory) {
            window.loadInventory = async function() {
                await originalLoadInventory.apply(this, arguments);
                
                // Cuando termina de cargar, añadir animaciones
                document.querySelectorAll('.tree-card').forEach(card => {
                    observer.observe(card);
                });
            };
        }
    }
    
    // Animación para el temporizador
    const timerDisplay = document.getElementById('timer');
    if (timerDisplay) {
        // Efecto de pulsación cada 10 segundos
        setInterval(() => {
            timerDisplay.classList.add('pulse');
            setTimeout(() => {
                timerDisplay.classList.remove('pulse');
            }, 1000);
        }, 10000);
    }
});