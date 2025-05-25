#!/usr/bin/env python3
"""
Script de migración para corregir la estructura de la base de datos:
1. Asegurar que los árboles de template estén en la colección 'trees'
2. Migrar los árboles de usuario para que estén en el array 'trees' de cada usuario
3. Eliminar árboles de usuario de la colección 'trees'

Ejecutar este script una sola vez para migrar los datos.
"""
from bson import ObjectId
from app.database import db
from datetime import datetime

def migrate_tree_templates():
    print("Iniciando migración de base de datos...")
    
    # 1. Asegurar que los árboles template estén en la colección 'trees'
    # Identificar árboles únicos por nombre para usarlos como plantillas
    pipeline = [
        {"$group": {"_id": "$name", "tree": {"$first": "$$ROOT"}}},
        {"$replaceRoot": {"newRoot": "$tree"}}
    ]
    
    unique_trees = list(db.trees.aggregate(pipeline))
    print(f"Se encontraron {len(unique_trees)} tipos de árboles únicos.")
    
    # Para cada árbol único, crear una plantilla en la colección 'trees'
    templates_created = 0
    for tree in unique_trees:
        # Verificar si ya existe una plantilla para este nombre de árbol
        existing_template = db.trees.find_one({
            "name": tree["name"],
            "is_template": True
        })
        
        if existing_template:
            print(f"Plantilla para '{tree['name']}' ya existe, actualizando...")
            # Actualizar la plantilla existente con la información más reciente
            db.trees.update_one(
                {"_id": existing_template["_id"]},
                {"$set": {
                    "category": tree.get("category", "Sin categoría"),
                    "description": tree.get("description", f"Plantilla de {tree['name']}"),
                    "image_url": tree.get("image_url", ""),
                    "updated_at": datetime.utcnow()
                }}
            )
        else:
            print(f"Creando nueva plantilla para '{tree['name']}'...")
            # Crear una nueva plantilla
            template = {
                "name": tree["name"],
                "category": tree.get("category", "Sin categoría"),
                "description": tree.get("description", f"Plantilla de {tree['name']}"),
                "image_url": tree.get("image_url", ""),
                "is_template": True,
                "created_at": datetime.utcnow()
            }
            
            db.trees.insert_one(template)
            templates_created += 1
    
    print(f"Migración de plantillas completada. {templates_created} nuevas plantillas creadas.")
    
    # 2. Migrar árboles de usuario a su colección correcta
    # Buscar árboles que no son plantillas en la colección 'trees'
    user_trees = list(db.trees.find({"is_template": {"$ne": True}, "user_id": {"$exists": True}}))
    print(f"Encontrados {len(user_trees)} árboles de usuario en la colección trees.")
    
    trees_migrated = 0
    users_updated = set()
    
    for tree in user_trees:
        user_id = tree.get("user_id")
        if not user_id:
            print(f"Árbol sin usuario: {tree['_id']}")
            continue
            
        # Crear el objeto de árbol para agregar al usuario
        tree_obj = {
            "_id": str(tree["_id"]),
            "name": tree["name"],
            "category": tree["category"],
            "description": tree.get("description", ""),
            "image_url": tree.get("image_url", "")
        }
        
        try:
            # Verificar si el árbol ya existe en el usuario
            user = db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                tree_exists = False
                for t in user.get("trees", []):
                    if str(t.get("_id")) == str(tree["_id"]):
                        tree_exists = True
                        break
                
                if not tree_exists:
                    # Añadir el árbol al array trees del usuario
                    result = db.users.update_one(
                        {"_id": ObjectId(user_id)},
                        {"$push": {"trees": tree_obj}}
                    )
                    
                    if result.modified_count > 0:
                        trees_migrated += 1
                        users_updated.add(user_id)
                        print(f"Árbol {tree['_id']} migrado al usuario {user_id}")
            else:
                print(f"Usuario {user_id} no encontrado")
        except Exception as e:
            print(f"Error al migrar árbol {tree['_id']}: {str(e)}")
    
    print(f"Migración de árboles completada. {trees_migrated} árboles migrados para {len(users_updated)} usuarios.")
    
    # 3. Actualizar estadísticas de usuarios
    for user_id in users_updated:
        try:
            # Contar árboles del usuario
            user = db.users.find_one({"_id": ObjectId(user_id)})
            if user and "trees" in user:
                tree_count = len(user["trees"])
                
                # Actualizar contador total_trees
                db.users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"total_trees": tree_count}}
                )
                print(f"Actualizado usuario {user_id} con {tree_count} árboles")
        except Exception as e:
            print(f"Error al actualizar estadísticas del usuario {user_id}: {str(e)}")
    
    print("Migración completada con éxito!")

if __name__ == "__main__":
    migrate_tree_templates()
    print("Migración completada exitosamente!")
    
    # Opcional: Eliminar árboles de usuario de la colección trees
    # Descomentar estas líneas si deseas eliminar los árboles duplicados
    # después de verificar que la migración fue exitosa
    """
    print("¿Deseas eliminar los árboles de usuario de la colección trees? (s/n)")
    respuesta = input().lower()
    if respuesta == 's' or respuesta == 'si':
        result = db.trees.delete_many({
            "is_template": {"$ne": True}, 
            "user_id": {"$exists": True}
        })
        print(f"Se eliminaron {result.deleted_count} árboles de usuario de la colección trees")
    else:
        print("No se eliminaron árboles. Puedes eliminarlos manualmente más tarde.")
    """
