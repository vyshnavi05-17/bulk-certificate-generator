from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.api.jobs import router as jobs_router
from app.api.certificates import router as certificates_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables are created at startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Bulk Certificate Generator API",
    description=(
        "Production-grade backend service for bulk certificate generation, "
        "asynchronous background job tracking, individual failure isolation, "
        "and certificate retrieval."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for cross-origin client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(jobs_router)
app.include_router(certificates_router)


@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Bulk Certificate Generator API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": {
            "create_job": "POST /api/jobs",
            "job_status": "GET /api/jobs/{job_id}",
            "job_download_all": "GET /api/jobs/{job_id}/download",
            "retrieve_certificate": "GET /api/certificates/{certificate_id}",
            "certificate_info": "GET /api/certificates/{certificate_id}/info"
        }
    }
