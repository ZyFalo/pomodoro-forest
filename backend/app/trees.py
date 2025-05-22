from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from bson import ObjectId
from app.auth import get_current_user
from app.database import db

router = APIRouter()

class Tree(BaseModel):
    name: str
    category: str
    image_url: str
    description: str

class TreeInDB(Tree):
    id: str

@router.get("/trees", response_model=List[TreeInDB])
async def get_trees(current_user = Depends(get_current_user)):
    user = db.users.find_one({"username": current_user["username"]})
    trees = []
    
    for tree in user.get("trees", []):
        trees.append({
            "id": tree["_id"],
            "name": tree["name"],
            "category": tree["category"],
            "image_url": tree["image_url"],
            "description": tree["description"]
        })
    
    return trees

@router.delete("/trees/{tree_id}")
async def delete_tree(tree_id: str, current_user = Depends(get_current_user)):
    try:
        # Convertir el string ID a ObjectId para MongoDB
        object_id = ObjectId(tree_id)
        
        # Eliminar SOLO el árbol con ese ID específico y que pertenezca al usuario
        result = db.trees.delete_one({
            "_id": object_id,
            "user_id": current_user["id"]  # Importante: solo eliminar árboles del usuario actual
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Árbol no encontrado o no tienes permiso para eliminarlo")
            
        return {"message": "Árbol eliminado correctamente"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de árbol inválido")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error al eliminar árbol: {str(e)}")

@router.put("/trees/{tree_id}")
async def update_tree(tree_id: str, tree: Tree, current_user = Depends(get_current_user)):
    # Primero verificamos si el árbol existe
    user = db.users.find_one({"username": current_user["username"]})
    tree_exists = False
    
    for t in user.get("trees", []):
        if t.get("_id") == tree_id:
            tree_exists = True
            break
    
    if not tree_exists:
        raise HTTPException(status_code=404, detail="Tree not found")
    
    # Actualizar el árbol
    db.users.update_one(
        {"username": current_user["username"], "trees._id": tree_id},
        {"$set": {
            "trees.$.name": tree.name,
            "trees.$.category": tree.category,
            "trees.$.image_url": tree.image_url,
            "trees.$.description": tree.description
        }}
    )
    
    return {"message": "Tree updated successfully"}
