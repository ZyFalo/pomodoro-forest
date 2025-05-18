from fastapi import APIRouter, Depends
from typing import Dict
from app.auth import get_current_user
from app.database import db

router = APIRouter()

@router.post("/user/stats/update")
async def update_user_stats(stats: Dict, current_user = Depends(get_current_user)):
    # Actualizar las estadísticas del usuario
    db.users.update_one(
        {"username": current_user["username"]},
        {"$set": {
            "pomodoros_completed": stats.get("pomodoros_completed", 0),
            "total_focus_minutes": stats.get("total_focus_minutes", 0)
        }}
    )
    return {"status": "Estadísticas actualizadas correctamente"}

@router.get("/user/stats")
async def get_user_stats(current_user = Depends(get_current_user)):
    # Obtener información del usuario
    user = db.users.find_one({"username": current_user["username"]})
    
    # Contar los árboles
    trees = user.get("trees", [])
    total_trees = len(trees)
    
    return {
        "total_trees": total_trees,
        "pomodoros_completed": user.get("pomodoros_completed", 0),
        "total_focus_minutes": user.get("total_focus_minutes", 0)
    }
