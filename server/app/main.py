from fastapi import FastAPI, UploadFile, File, HTTPException, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import PyPDF2
import io
from datetime import datetime
import base64
from urllib.parse import quote_plus
from app.services.ml_service import MLService
from pydantic import BaseModel
from starlette_prometheus import PrometheusMiddleware, metrics
from app.utils.logging_config import setup_logger
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from app.utils.metrics import (
    REQUESTS_TOTAL, REQUESTS_LATENCY, RESUME_UPLOADS,
    JOB_MATCHES, DB_OPERATIONS, API_INFO
)
import time

# Setup logging
logger = setup_logger()

# Create the main application
app = FastAPI(title="Career Navigator API")

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

# Create the API router
api_router = APIRouter(prefix="/api")

# Set API information for metrics
API_INFO.info({"version": "1.0", "name": "Career Navigator API"})

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Atlas connection
db_password = os.getenv('MONGODB_PASSWORD')
if not db_password:
    raise ValueError("MongoDB password not found in environment variables")

encoded_password = quote_plus(db_password)
uri = f"mongodb+srv://harikiran19062004_db_user:{encoded_password}@cluster0.csgbg0r.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.career_navigator

# Test the connection
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"Error connecting to MongoDB Atlas: {e}")

# Resume upload endpoint
@api_router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    start_time = time.time()
    try:
        logger.info(f"Receiving resume upload: {file.filename}")
        content = await file.read()
        
        # Extract text from PDF if applicable
        text = ""
        if file.filename.endswith('.pdf'):
            logger.info("Processing PDF file")
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        file_type = file.filename.split('.')[-1].lower()
        # Store the resume data in MongoDB
        resume_data = {
            "filename": file.filename,
            "file_content": content.decode() if file.filename.endswith('.txt') else content,
            "file_type": file_type,
            "content": text,
            "processed": False,
            "upload_date": datetime.utcnow()
        }
        
        # Update metrics
        RESUME_UPLOADS.labels(file_type=file_type).inc()
        REQUESTS_LATENCY.labels(path="/api/resume/upload", method="POST").observe(time.time() - start_time)
        
        result = db.resumes.insert_one(resume_data)
        
        return {
            "message": "Resume uploaded successfully",
            "id": str(result.inserted_id),
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Job matching endpoint
@api_router.get("/jobs/match/{resume_id}")
async def match_jobs(resume_id: str):
    start_time = time.time()
    try:
        logger.info(f"Starting job matching for resume ID: {resume_id}")
        # Get resume
        resume = db.resumes.find_one({"_id": ObjectId(resume_id)})
        if not resume:
            logger.error(f"Resume not found: {resume_id}")
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Update metrics
        JOB_MATCHES.inc()
        DB_OPERATIONS.labels(operation="find", collection="resumes").inc()
        
        # Get all jobs from the database
        jobs = list(db.jobs.find())
        if not jobs:
            # If no jobs exist, add sample jobs
            await add_sample_jobs()
            jobs = list(db.jobs.find())
        
        # Extract skills from resume
        resume_skills = ml_service.extract_skills(resume["content"])
        
        # Get job recommendations using ML service
        recommendations = ml_service.get_job_recommendations(
            resume_text=resume["content"],
            job_descriptions=jobs
        )
        
        # Update resume with extracted skills if not already processed
        if not resume.get("processed"):
            db.resumes.update_one(
                {"_id": ObjectId(resume_id)},
                {
                    "$set": {
                        "skills": resume_skills,
                        "processed": True
                    }
                }
            )
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add some sample jobs to the database
@api_router.post("/jobs/sample")
async def add_sample_jobs():
    try:
        sample_jobs = [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "description": """Looking for a skilled software engineer with strong expertise in Python development and modern web technologies. 
                The ideal candidate should have hands-on experience with:
                - Building scalable applications using Python and React
                - Implementing cloud solutions on AWS or similar platforms
                - Setting up and maintaining CI/CD pipelines
                - Writing clean, maintainable, and well-tested code
                - Working with RESTful APIs and microservices architecture""",
                "requirements": ["Python", "React", "AWS", "CI/CD", "REST APIs", "Microservices"]
            },
            {
                "title": "Full Stack Developer",
                "company": "Web Solutions Inc",
                "description": """We're seeking a Full Stack Developer proficient in modern web development technologies.
                Key responsibilities include:
                - Developing responsive web applications using React and Node.js
                - Designing and implementing MongoDB database schemas
                - Building RESTful APIs and real-time communication features
                - Implementing security best practices and user authentication
                - Collaborating with UX designers to implement intuitive interfaces""",
                "requirements": ["JavaScript", "Node.js", "React", "MongoDB", "REST APIs", "WebSocket"]
            },
            {
                "title": "ML Engineer",
                "company": "AI Innovations",
                "description": """Seeking an experienced Machine Learning Engineer to join our AI team.
                Required skills and experience:
                - Strong Python programming and data science skills
                - Expertise in deep learning frameworks like TensorFlow
                - Experience with NLP and text processing
                - Knowledge of machine learning deployment and MLOps
                - Familiarity with cloud-based ML platforms
                - Experience with large language models and transformers""",
                "requirements": ["Python", "TensorFlow", "NLP", "Deep Learning", "MLOps", "Cloud ML"]
            },
            {
                "title": "DevOps Engineer",
                "company": "Cloud Systems Inc",
                "description": """Looking for a DevOps Engineer to strengthen our infrastructure team.
                Key responsibilities:
                - Managing and automating cloud infrastructure on AWS/Azure
                - Implementing and maintaining CI/CD pipelines
                - Container orchestration with Kubernetes
                - Infrastructure as Code using Terraform
                - Monitoring and logging implementation
                - Security implementation and compliance""",
                "requirements": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "Security"]
            }
        ]
        
        result = db.jobs.insert_many(sample_jobs)
        return {"message": "Sample jobs added", "count": len(result.inserted_ids)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Initialize ML Service
ml_service = MLService()

class RoadmapRequest(BaseModel):
    resume_id: str
    target_role: str

@api_router.post("/career/roadmap")
async def get_career_roadmap(request: RoadmapRequest):
    try:
        resume = db.resumes.find_one({"_id": ObjectId(request.resume_id)})
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        roadmap = await ml_service.get_career_roadmap(resume["content"], request.target_role)
        if "error" in roadmap:
            raise HTTPException(status_code=500, detail=roadmap["error"])

        return roadmap

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/resume/download/{resume_id}")
async def download_resume(resume_id: str):
    try:
        resume = db.resumes.find_one({"_id": ObjectId(resume_id)})
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        # Convert bytes to base64 for binary files
        if isinstance(resume["file_content"], bytes):
            file_content = base64.b64encode(resume["file_content"]).decode()
        else:
            file_content = resume["file_content"]

        return {
            "filename": resume["filename"],
            "content": file_content,
            "file_type": resume["file_type"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Middleware for request tracking
@app.middleware("http")
async def track_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    # Update request metrics
    REQUESTS_TOTAL.labels(
        path=request.url.path,
        method=request.method
    ).inc()
    
    # Update latency metrics
    REQUESTS_LATENCY.labels(
        path=request.url.path,
        method=request.method
    ).observe(time.time() - start_time)
    
    return response

# Include the router
app.include_router(api_router)