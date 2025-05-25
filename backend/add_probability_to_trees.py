#!/usr/bin/env python3
"""
Script para añadir el campo de probabilidad (probability) a los árboles template
existentes en la base de datos.

Ejecutar este script una sola vez para actualizar la estructura.
"""
from app.database import db
import random
from datetime import datetime

def add_probability_to_trees():
    print("Iniciando actualización de árboles para añadir campo de probabilidad...")
    
    # 1. Buscar plantillas de árboles (templates)
    templates = list(db.trees.find({"is_template": True}))
    print(f"Se encontraron {len(templates)} plantillas de árboles.")
    
    # 2. Contar cuántos templates tienen ya el campo probability
    templates_with_probability = sum(1 for tree in templates if "probability" in tree)
    print(f"{templates_with_probability} plantillas ya tienen campo de probabilidad.")
    
    # 3. Actualizar las plantillas que no tienen probabilidad
    updated_count = 0
    for tree in templates:
        if "probability" not in tree:
            # Asignar una probabilidad aleatoria entre 5 y 25
            probability = random.uniform(5.0, 25.0)
            
            # Actualizar el árbol en la base de datos
            db.trees.update_one(
                {"_id": tree["_id"]},
                {"$set": {
                    "probability": probability,
                    "updated_at": datetime.utcnow()
                }}
            )
            updated_count += 1
            print(f"Árbol '{tree['name']}' actualizado con probabilidad {probability:.2f}")
    
    print(f"Se actualizaron {updated_count} plantillas de árboles.")
    
    # 4. Mostrar la distribución final de probabilidades
    templates = list(db.trees.find({"is_template": True}))
    total_probability = sum(tree.get("probability", 0) for tree in templates)
    
    print("\nDistribución de probabilidades:")
    for tree in templates:
        prob = tree.get("probability", 0)
        percentage = (prob / total_probability) * 100 if total_probability > 0 else 0
        print(f"- {tree['name']}: {prob:.2f} ({percentage:.2f}%)")
    
    print("\nActualización completada exitosamente!")

if __name__ == "__main__":
    add_probability_to_trees()
