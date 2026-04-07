from fastapi import FastAPI #web framework core
from fastapi.staticfiles import StaticFiles #lets backend and frontend run from same process
from database import Base, engine
from routers import upload, analysis

Base.metadata.create_all(bind=engine)
    #looks at the classes that inherit from base (Sample and Sequence) 
    #and makes corresponding Postgres table
app = FastAPI()
    #creates FastAPI instance that routers, endpoints, and middleware get attached to

app.include_router(upload.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
    #registers upload and analysis router with the app

app.mount("/static", StaticFiles(directory="static"), name="static")
    #puts everything in the static folder at the static url

@app.get("/")
def root():
    return {"status": "Genomics platform is running"}
    #when http://localhost:8000 is hit this status is returned