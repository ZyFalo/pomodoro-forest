#!/usr/bin/env python3
"""
Script de migración para marcar correctamente los árboles como plantillas
y asegurar la consistencia en la base de datos.

Ejecutar este script una sola vez para migrar los datos.
"""
from bson import ObjectId
from app.database import db
from datetime import datetime

def migrate_tree_templates():
    print("Iniciando migración de plantillas de árboles...")
    
    # 1. Identificar árboles únicos por nombre para usarlos como plantillas
    pipeline = [
        {"$group": {"_id": "$name", "tree": {"$first": "$$ROOT"}}},
        {"$replaceRoot": {"newRoot": "$tree"}}
    ]
    
    unique_trees = list(db.trees.aggregate(pipeline))
    print(f"Se encontraron {len(unique_trees)} tipos de árboles únicos.")
    
    # 2. Para cada árbol único, crear o actualizar una plantilla
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
            
            # Si hay un usuario_id en el árbol original, asignarlo a la plantilla
            if "user_id" in tree:
                template["user_id"] = tree["user_id"]
            
            db.trees.insert_one(template)
            templates_created += 1
    
    print(f"Migración completada. {templates_created} nuevas plantillas creadas.")
    
    # 3. Asegurarse de que todos los árboles de usuario tengan is_template=False
    result = db.trees.update_many(
        {"is_template": {"$exists": False}},
        {"$set": {"is_template": False}}
    )
    
    print(f"{result.modified_count} árboles de usuario actualizados con is_template=False")

if __name__ == "__main__":
    migrate_tree_templates()
    print("Migración completada exitosamente!")
