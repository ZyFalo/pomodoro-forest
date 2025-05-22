from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional
from pydantic import BaseModel
from bson import ObjectId
from app.auth import get_current_user
from app.database import db

router = APIRouter()

class TreeTemplate(BaseModel):
    name: str
    category: str
    image_url: str
    description: str

class TreeTemplateInDB(TreeTemplate):
    id: str

# Función auxiliar para verificar si un usuario es administrador
async def is_admin(current_user = Depends(get_current_user)):
    # Esta es una implementación simple, podrías expandirla según tus necesidades
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Se requieren privilegios de administrador")
    return current_user

@router.get("/admin/tree-templates", response_model=List[TreeTemplateInDB])
async def get_tree_templates(current_user = Depends(is_admin)):
    """
    Obtiene todos los templates de árboles disponibles (solo admin)
    """
    tree_templates = list(db.tree_types.find())
    
    # Transformar los objetos ObjectId a string para serialización JSON
    result = []
    for tree in tree_templates:
        result.append({
            "id": str(tree["_id"]),
            "name": tree["name"],
            "category": tree["category"],
            "description": tree["description"],
            "image_url": tree["image_url"]
        })
    
    return result

@router.post("/admin/tree-templates", response_model=TreeTemplateInDB)
async def create_tree_template(template: TreeTemplate, current_user = Depends(is_admin)):
    """
    Crea un nuevo template de árbol (solo admin)
    """
    new_template = {
        "name": template.name,
        "category": template.category,
        "description": template.description,
        "image_url": template.image_url
    }
    
    result = db.tree_types.insert_one(new_template)
    new_id = str(result.inserted_id)
    
    return {**template.dict(), "id": new_id}

@router.put("/admin/tree-templates/{template_id}", response_model=TreeTemplateInDB)
async def update_tree_template(template_id: str, template: TreeTemplate, current_user = Depends(is_admin)):
    """
    Actualiza un template de árbol existente (solo admin)
    """
    try:
        object_id = ObjectId(template_id)
        
        # Verificar que el template existe
        existing = db.tree_types.find_one({"_id": object_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Template de árbol no encontrado")
        
        # Actualizar el template
        db.tree_types.update_one(
            {"_id": object_id},
            {"$set": {
                "name": template.name,
                "category": template.category,
                "description": template.description,
                "image_url": template.image_url
            }}
        )
        
        return {**template.dict(), "id": template_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al actualizar template: {str(e)}")

@router.delete("/admin/tree-templates/{template_id}")
async def delete_tree_template(template_id: str, current_user = Depends(is_admin)):
    """
    Elimina un template de árbol (solo admin)
    """
    try:
        object_id = ObjectId(template_id)
        
        # Eliminar el template
        result = db.tree_types.delete_one({"_id": object_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Template de árbol no encontrado")
            
        return {"message": "Template de árbol eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al eliminar template: {str(e)}")