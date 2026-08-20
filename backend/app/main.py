from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.db.database import engine, Base

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Helmet Backend API")

# Configure CORS for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Smart Helmet Backend is running"}
