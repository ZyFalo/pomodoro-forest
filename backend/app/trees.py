from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from bson import ObjectId
from bson.errors import InvalidId
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
    try:
        # Buscar árboles en la colección trees (versión nueva)
        cursor = db.trees.find({"user_id": current_user["id"]})
        trees = []
        
        for tree in cursor:
            trees.append({
                "id": str(tree["_id"]),
                "name": tree["name"],
                "category": tree["category"],
                "image_url": tree["image_url"],
                "description": tree["description"]
            })
        
        # Si hay árboles, devolverlos directamente
        if trees:
            return trees
            
        # Si no hay árboles en la colección trees, buscar en el campo trees del usuario (versión antigua)
        user = db.users.find_one({"username": current_user["username"]})
        if user and "trees" in user:
            for tree in user.get("trees", []):
                trees.append({
                    "id": tree["_id"],
                    "name": tree["name"],
                    "category": tree["category"],
                    "image_url": tree["image_url"],
                    "description": tree["description"]
                })
            
        return trees
    except Exception as e:
        print(f"Error en get_trees: {e}")
        return []

@router.delete("/trees/{tree_id}")
async def delete_tree(tree_id: str, current_user = Depends(get_current_user)):
    try:
        # Asegurarnos de que tenemos un ID de usuario válido
        user_id = current_user.get("id")
        if not user_id:
            # Si no hay un id, intentamos usar _id como respaldo
            user_id = str(current_user.get("_id", ""))
            if not user_id:
                raise HTTPException(status_code=400, detail="ID de usuario no encontrado")
        
        # Convertir el string ID a ObjectId para MongoDB
        try:
            object_id = ObjectId(tree_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="ID de árbol inválido")
            
        # Registrar información para depuración
        print(f"Intentando eliminar árbol: {tree_id}, Usuario: {user_id}")
        
        # Intentar primero eliminar de la colección trees (enfoque nuevo)
        result = db.trees.delete_one({
            "_id": object_id,
            "user_id": user_id  # Importante: solo eliminar árboles del usuario actual
        })
        
        # Si se eliminó correctamente de la colección trees
        if result.deleted_count > 0:
            # También actualizar las estadísticas del usuario
            try:
                db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$inc": {"total_trees": -1}}
                )
            except Exception as e:
                print(f"Advertencia: No se pudo actualizar estadísticas: {str(e)}")
                
            return {"message": "Árbol eliminado correctamente"}
            
        # Si no se encontró en trees, intentar eliminar del array en users (enfoque antiguo)
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"trees": {"_id": tree_id}}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Árbol no encontrado o no tienes permiso para eliminarlo")
            
        return {"message": "Árbol eliminado correctamente"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Error al eliminar árbol: {str(e)}")
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
