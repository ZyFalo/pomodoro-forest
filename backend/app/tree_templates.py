from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional
from pydantic import BaseModel
from bson import ObjectId
from app.auth import get_current_user
from app.database import db
from datetime import datetime

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
    # Primero buscamos los marcados explícitamente como plantillas
    templates = list(db.trees.find({"is_template": True}))
    
    # Si tenemos plantillas explícitas, las devolvemos
    if templates and len(templates) > 0:
        result = []
        for tree in templates:
            result.append({
                "id": str(tree["_id"]),
                "name": tree["name"],
                "category": tree["category"],
                "description": tree["description"],
                "image_url": tree["image_url"]
            })
        return result
    
    # Plan B: Si no hay plantillas explícitas, usamos agrupación por nombre
    pipeline = [
        {"$group": {"_id": "$name", "tree": {"$first": "$$ROOT"}}},
        {"$replaceRoot": {"newRoot": "$tree"}},
        {"$project": {"_id": 1, "name": 1, "category": 1, "description": 1, "image_url": 1}}
    ]
    
    tree_templates = list(db.trees.aggregate(pipeline))
    
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
    # Asegurarnos de que el current_user tenga un campo id
    if "id" not in current_user and "_id" in current_user:
        # Convertir _id a id si es necesario
        current_user["id"] = str(current_user["_id"])
    
    if not current_user.get("id"):
        raise HTTPException(status_code=400, detail="ID de administrador no encontrado")
        
    # Verificar si ya existe un template con el mismo nombre
    existing = db.trees.find_one({
        "name": template.name,
        "is_template": True
    })
    
    if existing:
        # Actualizar en lugar de crear duplicado
        db.trees.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "category": template.category,
                "description": template.description,
                "image_url": template.image_url,
                "updated_at": datetime.utcnow()
            }}
        )
        return {**template.dict(), "id": str(existing["_id"])}
    
    # Si no existe, crear nuevo
    new_template = {
        "name": template.name,
        "category": template.category,
        "description": template.description,
        "image_url": template.image_url,
        "is_template": True,  # Marcamos como plantilla
        "user_id": current_user["id"],  # Asignamos al administrador como propietario
        "created_at": datetime.utcnow()
    }
    
    # Insertamos directamente en la colección trees
    result = db.trees.insert_one(new_template)
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
        existing = db.trees.find_one({"_id": object_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Template de árbol no encontrado")
        
        # Actualizar el template
        db.trees.update_one(
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
        result = db.trees.delete_one({"_id": object_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Template de árbol no encontrado")
            
        return {"message": "Template de árbol eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al eliminar template: {str(e)}")