from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict
import os
import tempfile

from .resume_parser import ResumeParser
from .matcher import ResumeMatcher

app = FastAPI(
    title="Smart Resume Screening System API",
    description="AI-powered resume screening API with skill matching and TF-IDF similarity",
    version="1.0.0"
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
parser = ResumeParser()
matcher = ResumeMatcher()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Smart Resume Screening System API",
        "endpoints": {
            "/": "This information",
            "/match": "POST - Upload resume and JD to get match score",
            "/health": "GET - Health check"
        },
        "usage": "POST to /match with resume PDF and job description",
        "frontend": "Use Streamlit app at http://localhost:8501"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.post("/match")
async def match_resume(
    resume_file: UploadFile = File(..., description="Resume PDF file"),
    job_description: str = File(..., description="Job description text")
):
    """
    Match a resume against a job description
    
    Returns:
        - match_score: 0-100 score
        - matched_skills: Skills found in both resume and JD
        - missing_skills: Skills required by JD but missing in resume
        - explanation: Brief explanation of the match
        - detailed_scores: Breakdown of scores
        - resume_metadata: Information about the resume
    """
    # Validate file type
    if not resume_file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        # Parse resume
        resume_data = parser.parse_resume(resume_file.file)
        # Provide canonical skills list to matcher for more accurate JD skill extraction
        resume_data['canonical_skills'] = parser.skills_list

        # Match against job description
        result = matcher.match_resume(resume_data, job_description)
        
        # Add resume metadata to response
        result["resume_metadata"] = {
            "filename": resume_file.filename,
            "skills_found": len(resume_data["skills"]),
            "experience_years": resume_data["experience"],
            "all_skills": resume_data["skills"]
        }
        
        return JSONResponse(
            status_code=200,
            content=result
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing resume: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)