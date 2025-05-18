from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import auth, trees, pomodoro, stats

app = FastAPI(title="Pomodoro Forest API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(trees.router, tags=["Trees"])
app.include_router(pomodoro.router, tags=["Pomodoro"])
app.include_router(stats.router, tags=["User Statistics"])

@app.get("/")
async def root():
    return {"message": "Welcome to Pomodoro Forest API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
