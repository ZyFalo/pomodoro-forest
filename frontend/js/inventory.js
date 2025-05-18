/**
 * Carga y muestra el inventario de árboles del usuario
 */
async function loadInventory() {
    try {
        // Mostrar spinner mientras carga
        const inventoryContainer = document.getElementById('inventory');
        inventoryContainer.innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="spinner-grow text-success" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-3 text-white">Cargando tu bosque...</p>
            </div>
        `;
        
        // Obtener los árboles del usuario
        const trees = await api.getTrees();
        console.log("Árboles recibidos:", trees);
        
        // Limpiar el contenedor
        inventoryContainer.innerHTML = '';
        const emptyMessage = document.getElementById('emptyInventory');
        
        // Si no hay árboles, mostrar mensaje
        if (!trees || trees.length === 0) {
            inventoryContainer.parentElement.parentElement.classList.add('d-none');
            emptyMessage.classList.remove('d-none');
            return;
        } else {
            inventoryContainer.parentElement.parentElement.classList.remove('d-none');
            emptyMessage.classList.add('d-none');
        }
        
        // Generar HTML para las tarjetas de árboles
        trees.forEach((tree, index) => {
            const treeCard = document.createElement('div');
            treeCard.className = 'col-md-6 col-lg-4 tree-item';
            treeCard.style.animationDelay = `${index * 100}ms`;
            
            treeCard.innerHTML = `
                <div class="tree-card">
                    <div class="tree-image-container">
                        <img src="${tree.image_url}" alt="${tree.name}" class="tree-image">
                        <div class="tree-badge">
                            <span class="badge">${tree.category}</span>
                        </div>
                    </div>
                    <div class="tree-content">
                        <h3 class="tree-name">${tree.name}</h3>
                        <p class="tree-description">${tree.description}</p>
                        <div class="tree-actions mt-3">
                            <button class="btn btn-sm btn-outline-success me-2" onclick="editDescription('${tree.id || tree._id}', '${tree.name}', '${tree.category}', '${tree.image_url}', '${tree.description.replace(/'/g, "\\'")}')">
                                <i class="bi bi-pencil-fill"></i> Personalizar
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="confirmDeleteTree('${tree.id || tree._id}', '${tree.name}')">
                                <i class="bi bi-trash-fill"></i> Eliminar
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            inventoryContainer.appendChild(treeCard);
        });
        
    } catch (error) {
        console.error('Error al cargar el inventario:', error);
        
        // Mostrar mensaje de error
        const inventoryContainer = document.getElementById('inventory');
        inventoryContainer.innerHTML = `
            <div class="col-12 text-center py-5">
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Error al cargar tu inventario. Por favor, intenta de nuevo.
                </div>
                <button class="btn btn-forest mt-3" onclick="loadInventory()">
                    <i class="bi bi-arrow-clockwise me-2"></i>Reintentar
                </button>
            </div>
        `;
    }
}

// Cargar el inventario cuando el documento esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Verificar si el usuario está autenticado
    if (!api.isAuthenticated()) { // Cambiado de isLoggedIn() a api.isAuthenticated()
        window.location.href = 'index.html';
        return;
    }
    
    // Cargar el inventario
    loadInventory();
});

/**
 * Muestra un modal de confirmación para eliminar un árbol
 */
function confirmDeleteTree(treeId, treeName) {
    // Crea el modal dinámicamente
    const modalHtml = `
        <div class="modal fade" id="deleteTreeModal" tabindex="-1" aria-labelledby="deleteTreeModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title" id="deleteTreeModalLabel">Confirmar eliminación</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p>¿Estás seguro de que deseas eliminar el árbol <strong>${treeName}</strong>?</p>
                        <p>Esta acción no se puede deshacer.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-danger" onclick="deleteTree('${treeId}')">Eliminar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Agrega el modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Muestra el modal
    const modal = new bootstrap.Modal(document.getElementById('deleteTreeModal'));
    modal.show();
    
    // Elimina el modal del DOM cuando se cierra
    document.getElementById('deleteTreeModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

/**
 * Elimina un árbol del inventario
 */
async function deleteTree(treeId) {
    try {
        // Intenta eliminar el árbol
        await api.deleteTree(treeId);
        
        // Cierra el modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteTreeModal'));
        modal.hide();
        
        // Muestra mensaje de éxito
        showToast('Árbol eliminado correctamente', 'success');
        
        // Recarga el inventario
        loadInventory();
    } catch (error) {
        console.error('Error al eliminar árbol:', error);
        showToast('Error al eliminar el árbol: ' + error.message, 'danger');
    }
}

/**
 * Muestra un modal para editar la descripción de un árbol
 */
function editDescription(treeId, name, category, imageUrl, description) {
    // Elimina cualquier modal anterior
    const existingModal = document.getElementById('editTreeModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Crea el modal dinámicamente con solo el campo de descripción editable
    const modalHtml = `
        <div class="modal fade" id="editTreeModal" tabindex="-1" aria-labelledby="editTreeModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title" id="editTreeModalLabel">Personalizar descripción</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editTreeForm">
                            <div class="mb-3">
                                <div class="card mb-3">
                                    <img src="${imageUrl}" class="card-img-top" alt="${name}" style="max-height: 200px; object-fit: cover;">
                                    <div class="card-body">
                                        <h5 class="card-title">${name}</h5>
                                        <span class="badge bg-success mb-2">${category}</span>
                                    </div>
                                </div>
                                
                                <label for="treeDescription" class="form-label">Descripción personalizada</label>
                                <textarea class="form-control" id="treeDescription" rows="3" placeholder="Describe tu conexión con este árbol...">${description}</textarea>
                                <div class="form-text">Puedes personalizar la descripción de tu árbol para hacerlo más especial.</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-success" onclick="updateTree('${treeId}')">Guardar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Agrega el modal al DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Muestra el modal
    const modal = new bootstrap.Modal(document.getElementById('editTreeModal'));
    modal.show();
    
    // Elimina el modal del DOM cuando se cierra
    document.getElementById('editTreeModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

/**
 * Actualiza un árbol en el servidor
 */
async function updateTree(treeId) {
    try {
        // Obtiene la nueva descripción del formulario
        const description = document.getElementById('treeDescription').value;
        
        // Valida los datos
        if (!description) {
            showToast('Por favor, completa la descripción', 'warning');
            return;
        }
        
        // Obtener los valores actuales del árbol del modal para enviar el objeto completo
        const name = document.querySelector('#editTreeModal .card-title').textContent;
        const category = document.querySelector('#editTreeModal .badge').textContent;
        const imageUrl = document.querySelector('#editTreeModal .card-img-top').src;
        
        // Mostrar estado de carga
        const saveButton = document.querySelector('#editTreeModal .modal-footer .btn-success');
        const originalText = saveButton.innerHTML;
        saveButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...';
        saveButton.disabled = true;
        
        // Prepara los datos para la actualización (objeto Tree completo)
        const treeData = { 
            name: name,
            category: category, 
            image_url: imageUrl,
            description: description
        };
        
        console.log('Enviando actualización de árbol:', treeId, treeData);
        
        // Intenta actualizar el árbol
        await api.updateTree(treeId, treeData);
        
        // Cierra el modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('editTreeModal'));
        modal.hide();
        
        // Muestra mensaje de éxito
        showToast('Descripción actualizada correctamente', 'success');
        
        // Recarga el inventario
        loadInventory();
    } catch (error) {
        console.error('Error al actualizar árbol:', error);
        showToast('Error al actualizar la descripción: ' + (error.message || 'Error desconocido'), 'danger');
        
        // Restaurar el botón
        const saveButton = document.querySelector('#editTreeModal .modal-footer .btn-success');
        if (saveButton) {
            saveButton.innerHTML = 'Guardar';
            saveButton.disabled = false;
        }
    }
}

/**
 * Muestra un toast con un mensaje
 */
function showToast(message, type = 'info') {
    // Crea el toast dinámicamente
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    // Verifica si existe el contenedor de toasts
    let toastContainer = document.querySelector('.toast-container');
    
    // Si no existe, créalo
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Agrega el toast al contenedor
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Muestra el toast
    const toast = new bootstrap.Toast(document.getElementById(toastId), {
        autohide: true,
        delay: 3000
    });
    toast.show();
    
    // Elimina el toast del DOM cuando se oculta
    document.getElementById(toastId).addEventListener('hidden.bs.toast', function () {
        this.remove();
        
        // Si no hay más toasts, elimina el contenedor
        if (toastContainer.children.length === 0) {
            toastContainer.remove();
        }
    });
}
