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
    Si no hay tipos de árboles en la base de datos, se devuelven algunos árboles predeterminados.
    """
    # Buscar todos los tipos de árboles en la base de datos
    tree_types = list(db.tree_types.find())
    
    # Si no hay tipos de árboles en la base de datos, crear algunos predeterminados
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
        
        # Insertar los árboles predeterminados en la base de datos
        db.tree_types.insert_many(default_trees)
        tree_types = default_trees
    
    # Transformar los objetos ObjectId a string para serialización JSON
    for tree in tree_types:
        if "_id" in tree:
            tree["_id"] = str(tree["_id"])
    
    return tree_types

@router.post("/complete-pomodoro")
async def complete_pomodoro(current_user = Depends(get_current_user)):
    try:
        # Obtener todos los tipos de árboles disponibles
        tree_types = await get_tree_types(current_user)
        
        # Seleccionar un árbol aleatorio de la lista de la base de datos
        tree_data = random.choice(tree_types)
        
        # Crear un nuevo árbol con un ID único generado por MongoDB
        new_tree = {
            # No definir _id aquí, MongoDB lo generará automáticamente
            "user_id": current_user["id"],
            "name": tree_data["name"],
            "category": tree_data["category"],
            "description": tree_data["description"],
            "image_url": tree_data["image_url"],
            "created_at": datetime.now()
        }
        
        # Insertar en la base de datos (MongoDB generará un _id único automáticamente)
        result = db.trees.insert_one(new_tree)
        
        # Obtener el ID generado por MongoDB
        new_tree_id = str(result.inserted_id)
        
        # Actualizar las estadísticas del usuario
        db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$inc": {"pomodoros_completed": 1, "total_trees": 1}}
        )
        
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
        raise HTTPException(status_code=500, detail=f"Error al completar el pomodoro: {str(e)}")
