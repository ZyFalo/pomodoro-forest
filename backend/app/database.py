from pymongo import MongoClient
import os

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://williampena:1006506574@cluster0.zgcor.mongodb.net/")
client = MongoClient(MONGO_URI)
db = client["pomodoro_forest"]
