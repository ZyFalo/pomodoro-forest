from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.auth import get_current_user
from app.scrapers.frases_scraper import obtener_frase_del_dia
from app.scrapers.audio_scraper import obtener_audio_bosque
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
    
    frase = obtener_frase_del_dia()
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
    frase = obtener_frase_del_dia()
    if not frase:
        frase = "¡Cada minuto cuenta en tu camino hacia el éxito!"
    return {"phrase": frase}

@router.post("/complete-pomodoro")
async def complete_pomodoro(current_user = Depends(get_current_user)):
    # Verificar si existe la colección "trees" en la base de datos
    # y crearla con árboles predefinidos si no existe
    try:
        # Verificar si ya existe la colección de árboles
        if "trees" not in db.list_collection_names():
            # Lista de árboles predefinidos para insertar en la colección
            default_trees = [
                {
                    "name": "Roble",
                    "category": "Bosque",
                    "image_url": "https://cdn.pixabay.com/photo/2015/03/07/10/00/oak-tree-662500_640.jpg",
                    "description": "Un majestuoso roble, símbolo de fuerza y perseverancia."
                },
                {
                    "name": "Pino",
                    "category": "Bosque",
                    "image_url": "https://cdn.pixabay.com/photo/2016/02/13/12/26/tree-1197911_640.jpg",
                    "description": "Un alto pino verde, representa la longevidad y sabiduría."
                },
                {
                    "name": "Cerezo",
                    "category": "Floración",
                    "image_url": "https://cdn.pixabay.com/photo/2018/04/27/09/23/cherry-blossoms-3354934_640.jpg",
                    "description": "Un hermoso cerezo en flor, símbolo de la belleza efímera y la renovación."
                },
                {
                    "name": "Arce",
                    "category": "Otoño",
                    "image_url": "https://cdn.pixabay.com/photo/2015/11/07/11/25/autumn-1031286_640.jpg",
                    "description": "Un arce con hojas rojas, perfecto para representar el cambio y adaptación."
                },
                {
                    "name": "Sauce Llorón",
                    "category": "Agua",
                    "image_url": "https://cdn.pixabay.com/photo/2013/05/07/13/40/weeping-willow-109287_640.jpg",
                    "description": "Un sauce llorón que crece junto al agua, símbolo de flexibilidad y resiliencia."
                },
                {
                    "name": "Secuoya",
                    "category": "Antiguo",
                    "image_url": "https://cdn.pixabay.com/photo/2017/07/05/15/30/sequoia-2474953_640.jpg",
                    "description": "Una imponente secuoya, representa grandeza y resistencia."
                }
            ]
            
            # Insertar los árboles en la colección
            db.trees.insert_many(default_trees)
            print("Colección de árboles creada con éxito.")
    except Exception as e:
        print(f"Error al crear la colección de árboles: {str(e)}")

    # Ahora, en lugar de tener la lista de árboles hardcodeada,
    # obtenemos los árboles de la colección de la base de datos
    try:
        trees = list(db.trees.find({}, {"_id": 1, "name": 1, "category": 1, "image_url": 1, "description": 1}))
        
        # Convertir ObjectId a string para que sea serializable
        for tree in trees:
            tree["_id"] = str(tree["_id"])
            
        if not trees:
            # Si no hay árboles en la colección (caso muy raro), usamos una lista predefinida
            trees = [
                {
                    "_id": str(ObjectId()),
                    "name": "Roble Predeterminado",
                    "category": "Bosque",
                    "image_url": "https://cdn.pixabay.com/photo/2015/03/07/10/00/oak-tree-662500_640.jpg",
                    "description": "Un árbol predeterminado cuando no hay árboles en la base de datos."
                }
            ]
        
        # Seleccionar un árbol aleatorio
        tree = random.choice(trees)
        
        # Guardar el árbol en el inventario del usuario
        db.users.update_one(
            {"username": current_user["username"]},
            {"$push": {"trees": tree}}
        )
        
        return {
            "message": "¡Felicidades! Has completado un pomodoro.",
            "tree": {
                "id": tree["_id"],
                "name": tree["name"],
                "category": tree["category"],
                "image_url": tree["image_url"],
                "description": tree["description"]
            }
        }
    except Exception as e:
        return {"error": f"Error al completar pomodoro: {str(e)}"}
