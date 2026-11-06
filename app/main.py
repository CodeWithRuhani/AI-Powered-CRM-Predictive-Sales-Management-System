from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config import settings,ROOT
from app.database import Base,engine
from app import models
from app.routes import router
Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.APP_NAME,version='1.0.0',description='Predictive CRM with Ollama assistant and Scikit-learn lead scoring.')
app.include_router(router)
app.mount('/static',StaticFiles(directory=ROOT/'frontend'),name='static')
@app.get('/',include_in_schema=False)
def home():return FileResponse(ROOT/'frontend'/'index.html')
