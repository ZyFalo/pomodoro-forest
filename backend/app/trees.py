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
        user_id = current_user.get("id")
        if not user_id and "_id" in current_user:
            user_id = str(current_user["_id"])
        
        # Buscar el usuario por ID
        user = db.users.find_one({"_id": ObjectId(user_id)})
        
        trees = []
        if user and "trees" in user:
            # Obtener los árboles directamente del campo trees del usuario
            for tree in user.get("trees", []):
                trees.append({
                    "id": tree["_id"],
                    "name": tree["name"],
                    "category": tree["category"],
                    "image_url": tree["image_url"],
                    "description": tree["description"]
                })
        
        # Registramos información para depuración
        print(f"Obtenidos {len(trees)} árboles para el usuario {user_id}")
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
            
        # Registrar información para depuración
        print(f"Intentando eliminar árbol: {tree_id}, Usuario: {user_id}")
        
        # Eliminar el árbol del array trees del usuario
        result = db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$pull": {"trees": {"_id": tree_id}},
                "$inc": {"total_trees": -1}  # Actualizar contador de árboles
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Árbol no encontrado o no tienes permiso para eliminarlo")
            
        # Registrar éxito
        print(f"Árbol {tree_id} eliminado correctamente del usuario {user_id}")
        return {"message": "Árbol eliminado correctamente"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Error al eliminar árbol: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar árbol: {str(e)}")

@router.put("/trees/{tree_id}")
async def update_tree(tree_id: str, tree: Tree, current_user = Depends(get_current_user)):
    # Obtenemos el ID del usuario
    user_id = current_user.get("id")
    if not user_id and "_id" in current_user:
        user_id = str(current_user["_id"])
    
    # Buscar el usuario por ID
    user = db.users.find_one({"_id": ObjectId(user_id)})
    tree_exists = False
    
    # Verificar si el árbol existe en el array trees del usuario
    if user and "trees" in user:
        for t in user["trees"]:
            if str(t.get("_id")) == tree_id:
                tree_exists = True
                break
    
    if not tree_exists:
        raise HTTPException(status_code=404, detail="Árbol no encontrado en tu inventario")
    
    # Actualizar el árbol en el array trees del usuario
    result = db.users.update_one(
        {"_id": ObjectId(user_id), "trees._id": tree_id},
        {"$set": {
            "trees.$.name": tree.name,
            "trees.$.category": tree.category,
            "trees.$.image_url": tree.image_url,
            "trees.$.description": tree.description
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el árbol")
    
    print(f"Árbol {tree_id} del usuario {user_id} actualizado correctamente")
    return {"message": "Árbol actualizado correctamente"}
