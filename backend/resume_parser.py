import re
import PyPDF2
from typing import Dict, List, Optional
import spacy

# Load spaCy model for NLP (will download if not present)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

class ResumeParser:
    """Basic resume parser to extract skills and experience"""
    
    def __init__(self):
        # Common technical skills list (can be expanded)
        self.skills_list = [
            "python", "java", "javascript", "react", "angular", "vue", "node.js",
            "django", "flask", "spring", "spring boot", "c++", "c#", "ruby",
            "php", "swift", "kotlin", "typescript", "html", "css", "sass",
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
            "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git",
            "linux", "unix", "machine learning", "deep learning", "nlp",
            "computer vision", "pandas", "numpy", "scikit-learn", "tensorflow",
            "pytorch", "keras", "tableau", "power bi", "excel", "spark",
            "hadoop", "kafka", "rabbitmq", "graphql", "rest api", "microservices",
            "agile", "scrum", "leadership", "communication", "teamwork",
            "problem solving", "critical thinking", "project management"
        ]
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file object"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text.lower()
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text using keyword matching"""
        found_skills = []
        text_lower = text.lower()
        
        for skill in self.skills_list:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in found_skills:
            if skill not in seen:
                seen.add(skill)
                unique_skills.append(skill)
        
        return unique_skills
    
    def extract_experience(self, text: str) -> Optional[float]:
        """Extract years of experience from resume text"""
        # Pattern to find experience mentions
        patterns = [
            r'(\d+)\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience\s*(?:of)?\s*(\d+)\s*\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:professional)?\s*experience',
            r'total experience\s*(?:of)?\s*(\d+)\s*\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*\+\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience:\s*(\d+)\s*\+?\s*(?:years?|yrs?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    def parse_resume(self, pdf_file) -> Dict:
        """Main method to parse resume and extract information"""
        text = self.extract_text_from_pdf(pdf_file)
        
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        
        return {
            "skills": skills,
            "experience": experience,
            "full_text": text
        }