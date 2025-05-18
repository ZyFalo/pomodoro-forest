import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from bson import ObjectId
import json

# Importar scrapers
from app.scrapers.frases_scraper import obtener_frase_del_dia
from app.scrapers.audio_scraper import obtener_audio_bosque

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://williampena:1006506574@cluster0.zgcor.mongodb.net/")
client = MongoClient(MONGO_URI)
db = client["pomodoro_forest"]

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize FastAPI
app = FastAPI(title="Pomodoro Forest API")

# Configurar CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:3000",
    "https://pomodoro-forest.vercel.app",  # Si planeas desplegar el frontend en Vercel
    "*",  # Permite todas las origins en desarrollo (quitar en producción)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Al inicio de la aplicación, agregar script de migración
@app.on_event("startup")
async def initialize_database():
    # Asegurar que todos los usuarios tengan campos de estadísticas
    db.users.update_many(
        {"pomodoros_completed": {"$exists": False}},
        {"$set": {"pomodoros_completed": 0}}
    )
    db.users.update_many(
        {"total_focus_minutes": {"$exists": False}},
        {"$set": {"total_focus_minutes": 0}}
    )
    print("Base de datos inicializada: campos de estadísticas configurados")

# Models
class User(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserInDB(User):
    hashed_password: str
    trees: List[str] = []

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PomodoroSettings(BaseModel):
    duration: int = 25  # Default 25 minutes

class Tree(BaseModel):
    name: str
    category: str
    image_url: str
    description: str

class TreeInDB(Tree):
    id: str

# Helper functions
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    user_data = db.users.find_one({"username": username})
    if user_data:
        return user_data
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Endpoints
@app.post("/register", response_model=Token)
async def register_user(user: User):
    db_user = get_user(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "hashed_password": hashed_password,
        "email": user.email,
        "trees": [],
        # Añadir campos de estadísticas inicializados
        "pomodoros_completed": 0,
        "total_focus_minutes": 0
    }
    
    result = db.users.insert_one(user_data)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/start-pomodoro")
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

@app.get("/motivational-phrase")
async def get_motivational_phrase(current_user = Depends(get_current_user)):
    frase = obtener_frase_del_dia()
    if not frase:
        frase = "¡Cada minuto cuenta en tu camino hacia el éxito!"
    return {"phrase": frase}

@app.post("/complete-pomodoro")
async def complete_pomodoro(current_user = Depends(get_current_user)):
    # Lista de árboles predefinidos
    trees = [
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
            "image_url": "https://cdn.pixabay.com/photo/2017/03/14/11/41/cherry-blossom-2143502_640.jpg",
            "description": "Un hermoso cerezo en flor, símbolo de la belleza efímera y renovación."
        },
        {
            "name": "Sauce Llorón",
            "category": "Agua",
            "image_url": "https://cdn.pixabay.com/photo/2013/11/28/09/58/weeping-willow-219976_640.jpg",
            "description": "Un elegante sauce llorón, refleja tranquilidad y adaptabilidad."
        },
        {
            "name": "Secuoya",
            "category": "Gigante",
            "image_url": "https://cdn.pixabay.com/photo/2017/07/05/15/30/sequoia-2474953_640.jpg",
            "description": "Una imponente secuoya, representa grandeza y resistencia."
        }
    ]
    
    # Seleccionar un árbol aleatorio
    import random
    tree = random.choice(trees)
    tree["_id"] = str(ObjectId())
    
    # Guardar el árbol en el inventario del usuario
    db.users.update_one(
        {"username": current_user["username"]},
        {"$push": {"trees": tree}}
    )
    
    # También actualizar las estadísticas del usuario
    db.users.update_one(
        {"username": current_user["username"]},
        {"$inc": {
            "pomodoros_completed": 1,
            "total_focus_minutes": 25  # Asumimos que cada pomodoro es de 25 minutos por defecto
        }}
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

@app.get("/trees")
async def get_trees(current_user = Depends(get_current_user)):
    user = get_user(current_user["username"])
    return {"trees": user.get("trees", [])}

@app.delete("/trees/{tree_id}")
async def delete_tree(tree_id: str, current_user = Depends(get_current_user)):
    result = db.users.update_one(
        {"username": current_user["username"]},
        {"$pull": {"trees": {"_id": tree_id}}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Tree not found")
    
    return {"message": "Tree deleted successfully"}

@app.put("/trees/{tree_id}")
async def update_tree(tree_id: str, tree: Tree, current_user = Depends(get_current_user)):
    # Primero verificamos si el árbol existe
    user = get_user(current_user["username"])
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

@app.post("/user/stats/update")
async def update_user_stats(stats: dict, current_user = Depends(get_current_user)):
    # Actualizar las estadísticas del usuario
    db.users.update_one(
        {"username": current_user["username"]},
        {"$set": {
            "pomodoros_completed": stats.get("pomodoros_completed", 0),
            "total_focus_minutes": stats.get("total_focus_minutes", 0)
        }}
    )
    return {"status": "Estadísticas actualizadas correctamente"}

@app.get("/user/stats")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
