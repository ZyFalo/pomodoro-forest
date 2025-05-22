from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.auth import get_current_user
from app.scrapers.frases_scraper import obtener_frase_del_dia
from app.scrapers.audio_scraper import obtener_audio_bosque
from app.scrapers.frases_scraper import obtener_frase_aleatoria_siempre
from app.database import db
from bson import ObjectId
import random

router = APIRouter()

class PomodoroSettings(BaseModel):
    duration: int = 25  # Default 25 minutes

@router.post("/start-pomodoro")
async def start_pomodoro(settings: PomodoroSettings, current_user = Depends(get_current_user)):
    audio_url = obtener_audio_bosque()
    if not audio_url:
        audio_url = "https://assets.mixkit.co/sfx/preview/mixkit-forest-stream-ambience-loop-542.mp3"  # Fallback audio
    
    # Usar obtener_frase_aleatoria_siempre en lugar de obtener_frase_del_dia
    frase = obtener_frase_aleatoria_siempre()
    if not frase:
        frase = "¡El tiempo es oro! Aprovéchalo al máximo."  # Fallback phrase
    
    end_time = datetime.utcnow() + timedelta(minutes=settings.duration)
    
    return {
        "end_time": end_time.isoformat(),
        "duration": settings.duration,
        "audio_url": audio_url,
        "motivational_phrase": frase
    }

@router.get("/motivational-phrase")
async def get_motivational_phrase(current_user = Depends(get_current_user)):
    # Usar la función mejorada para siempre obtener una frase aleatoria
    # que no se repite con respecto a la anterior
    frase = obtener_frase_aleatoria_siempre()
    
    # Asegurarnos de que la frase no esté vacía
    if not frase or frase.strip() == "":
        frase = "¡Sigue adelante! Cada minuto de concentración te acerca a tus metas."
        
    return {"phrase": frase}

@router.get("/tree-types")
async def get_tree_types(current_user = Depends(get_current_user)):
    """
    Obtiene una lista de todos los tipos de árboles disponibles en la base de datos.
    """
    # Primero buscamos árboles marcados explícitamente como plantillas
    template_trees = list(db.trees.find({"is_template": True}))
    
    # Si encontramos plantillas, las usamos
    if template_trees and len(template_trees) > 0:
        tree_types = template_trees
    else:
        # Plan B: Si no hay plantillas explícitas, usamos la agrupación por nombre
        pipeline = [
            {"$group": {"_id": "$name", "tree": {"$first": "$$ROOT"}}},
            {"$replaceRoot": {"newRoot": "$tree"}},
            {"$project": {"_id": 1, "name": 1, "category": 1, "description": 1, "image_url": 1}}
        ]
        
        trees_cursor = db.trees.aggregate(pipeline)
        tree_types = list(trees_cursor)
    
    # Si aun así no hay árboles en la colección, usamos árboles predeterminados
    if not tree_types:
        default_trees = [
            {
                "name": "Pino",
                "category": "Coníferas",
                "description": "Un majestuoso pino que simboliza tu enfoque y resistencia.",
                "image_url": "https://cdn-icons-png.flaticon.com/512/628/628283.png"
            },
            {
                "name": "Roble",
                "category": "Caducifolios",
                "description": "Un fuerte roble que representa la solidez de tu trabajo.",
                "image_url": "https://cdn-icons-png.flaticon.com/512/1245/1245042.png"
            },
            {
                "name": "Cerezo",
                "category": "Florales",
                "description": "Un hermoso cerezo en flor que simboliza el progreso y la belleza de tu esfuerzo.",
                "image_url": "https://cdn-icons-png.flaticon.com/512/1466/1466332.png"
            },
            {
                "name": "Palmera",
                "category": "Tropicales",
                "description": "Una palmera tropical que representa la calma y el equilibrio en tu trabajo.",
                "image_url": "https://cdn-icons-png.flaticon.com/512/2826/2826838.png"
            },
            {
                "name": "Sauce",
                "category": "Ribereños",
                "description": "Un tranquilo sauce que simboliza la flexibilidad y adaptabilidad.",
                "image_url": "https://cdn-icons-png.flaticon.com/512/1466/1466538.png"
            }
        ]
        
        # En lugar de insertar en tree_types, simplemente devolvemos los árboles predeterminados
        tree_types = default_trees
    
    # Transformar los objetos ObjectId a string para serialización JSON
    for tree in tree_types:
        if "_id" in tree:
            tree["_id"] = str(tree["_id"])
    
    return tree_types

@router.post("/complete-pomodoro")
async def complete_pomodoro(current_user = Depends(get_current_user)):
    try:
        # Asegurarnos de que el current_user tenga un campo id
        if "id" not in current_user and "_id" in current_user:
            # Convertir _id a id si es necesario
            current_user["id"] = str(current_user["_id"])
        
        if "id" not in current_user or not current_user["id"]:
            raise HTTPException(status_code=400, detail="Error de autenticación: ID de usuario no encontrado")
            
        # Log para depuración
        print(f"Completando pomodoro para usuario: {current_user['id']}")
        
        # Obtener todos los tipos de árboles disponibles
        tree_types = await get_tree_types(current_user)
        
        # Comprobar si se obtuvieron tipos de árboles
        if not tree_types or len(tree_types) == 0:
            print("No se encontraron tipos de árboles, usando árboles predeterminados")
            # Si llegamos aquí, usamos árboles predeterminados como último recurso
            tree_types = [
                {
                    "name": "Pino",
                    "category": "Coníferas",
                    "description": "Un majestuoso pino que simboliza tu enfoque y resistencia.",
                    "image_url": "https://cdn-icons-png.flaticon.com/512/628/628283.png"
                }
            ]
            
        # Seleccionar un árbol aleatorio de la lista
        tree_data = random.choice(tree_types)
        
        # Crear un nuevo árbol con un ID único generado por MongoDB
        new_tree = {
            "user_id": current_user["id"],
            "name": tree_data.get("name", "Árbol"),
            "category": tree_data.get("category", "General"),
            "description": tree_data.get("description", "Un nuevo árbol en tu bosque"),
            "image_url": tree_data.get("image_url", "https://cdn-icons-png.flaticon.com/512/628/628283.png"),
            "created_at": datetime.now(),
            "is_template": False  # Marcar explícitamente como árbol de usuario, no plantilla
        }
        
        # Insertar en la base de datos (MongoDB generará un _id único automáticamente)
        result = db.trees.insert_one(new_tree)
        
        # Obtener el ID generado por MongoDB
        new_tree_id = str(result.inserted_id)
        
        # Log para depuración
        print(f"Árbol creado con ID: {new_tree_id}")
        
        # Actualizar las estadísticas del usuario
        try:
            db.users.update_one(
                {"_id": ObjectId(current_user["id"])},
                {"$inc": {"pomodoros_completed": 1, "total_trees": 1}}
            )
        except Exception as e:
            print(f"Advertencia: No se pudieron actualizar estadísticas: {str(e)}")
            # Continuamos aunque falle la actualización de estadísticas
        
        # Devolver el árbol con su ID para mostrar al usuario
        return {
            "message": "Pomodoro completado exitosamente",
            "tree": {
                "id": new_tree_id,  # Importante: devolver el ID único
                "name": new_tree["name"],
                "category": new_tree["category"],
                "description": new_tree["description"],
                "image_url": new_tree["image_url"]
            }
        }
    except Exception as e:
        print(f"Error al completar el pomodoro: {str(e)}")
        # Proporcionar error más detallado para depuración
        import traceback
        error_details = traceback.format_exc()
        print(error_details)
        
        raise HTTPException(status_code=500, detail=f"Error al completar el pomodoro: {str(e)}")
