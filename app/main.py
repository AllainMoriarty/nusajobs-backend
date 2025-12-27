from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn
import logging
from app.core.database import Base, engine
from app.routers import company, job, candidate, candidate_preference, candidate_cv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

bearer_scheme = HTTPBearer()

app = FastAPI(title="Jobless API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Jobless API",
        version="1.0",
        routes=app.routes,
    )

    # Tambahkan securitySchemes tanpa menghapus schema lain
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    if "securitySchemes" not in openapi_schema["components"]:
        openapi_schema["components"]["securitySchemes"] = {}

    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "apiKey",
        "name": "Authorization",
        "in": "header",
        "description": "JWT Authorization header using the Bearer scheme. \n\nEnter 'Bearer' [space] and then your token in the text input below. Example: `Bearer 12345abcdef`"
    }

    # Tambahkan security global
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(company.router)
app.include_router(job.router)
app.include_router(candidate.router)
app.include_router(candidate_preference.router)
app.include_router(candidate_cv.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Jobless API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)