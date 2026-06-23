import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple
import re

class ResumeMatcher:
    """Match resumes against job description using TF-IDF and skill matching"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
    
    def extract_skills_from_jd(self, jd_text: str, skill_list: List[str]) -> List[str]:
        """Extract required skills from job description"""
        jd_lower = jd_text.lower()
        required_skills = []

        # Normalize JD text for more accurate matching
        jd_normalized = re.sub(r'[\W_]+', ' ', jd_lower)

        for skill in skill_list:
            norm_skill = self._normalize_skill(skill)
            # Match by whole words or phrases using normalized forms
            if norm_skill and re.search(rf"\b{re.escape(norm_skill)}\b", jd_normalized):
                required_skills.append(skill)

        return required_skills

    def _normalize_skill(self, s: str) -> str:
        """Normalize a skill string for comparison: lower, remove punctuation, dots, pluses"""
        if not s:
            return ""
        s = s.lower()
        s = s.replace('.', ' ')
        s = s.replace('+', ' plus ')
        s = re.sub(r"[^a-z0-9\s]", ' ', s)
        s = re.sub(r"\s+", ' ', s).strip()
        return s
    
    def calculate_skill_match(self, resume_skills: List[str], jd_skills: List[str]) -> Tuple[float, List[str], List[str]]:
        """Calculate skill match percentage and identify matched/missing skills"""
        if not jd_skills:
            return 100.0, [], []

        # Build normalized sets for robust matching
        resume_norm = {self._normalize_skill(s): s for s in resume_skills}
        jd_norm = {self._normalize_skill(s): s for s in jd_skills}

        matched_skills = []
        missing_skills = []

        for jd_norm_key, jd_orig in jd_norm.items():
            if not jd_norm_key:
                continue

            # Direct normalized match
            if jd_norm_key in resume_norm:
                matched_skills.append(jd_orig)
                continue

            # Partial token overlap: check if any resume skill tokens appear in jd skill
            jd_tokens = set(jd_norm_key.split())
            found = False
            for res_norm_key, res_orig in resume_norm.items():
                res_tokens = set(res_norm_key.split())
                # If majority of tokens overlap, count as match
                if jd_tokens and len(jd_tokens & res_tokens) / len(jd_tokens) >= 0.5:
                    matched_skills.append(jd_orig)
                    found = True
                    break

            if not found:
                missing_skills.append(jd_orig)

        skill_score = (len(matched_skills) / len(jd_skills)) * 100 if jd_skills else 0
        return skill_score, matched_skills, missing_skills
    
    def calculate_tfidf_similarity(self, resume_text: str, jd_text: str) -> float:
        """Calculate TF-IDF cosine similarity between resume and job description"""
        # Combine texts for fitting
        documents = [resume_text, jd_text]
        
        # Fit and transform
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        
        return similarity[0][0] * 100
    
    def calculate_experience_score(self, resume_exp: float, jd_text: str) -> float:
        """Calculate experience match score based on JD requirements"""
        if resume_exp is None:
            return 0.0
        
        # Extract experience requirement from JD
        exp_patterns = [
            r'(\d+)\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience\s*(?:of)?\s*(\d+)\s*\+?\s*(?:years?|yrs?)',
            r'minimum\s*(?:of)?\s*(\d+)\s*\+?\s*(?:years?|yrs?)',
            r'at least\s*(\d+)\s*\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*\+\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience:\s*(\d+)\s*\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*\+?\s*years?.*?(?:required|preferred|experience)'
        ]
        
        required_exp = None
        for pattern in exp_patterns:
            match = re.search(pattern, jd_text, re.IGNORECASE)
            if match:
                try:
                    required_exp = float(match.group(1))
                    break
                except ValueError:
                    continue
        
        if required_exp is None:
            return 100.0  # No experience requirement specified
        
        # Calculate score (exponential decay for experience below requirement)
        if resume_exp >= required_exp:
            return 100.0
        else:
            # Score decreases exponentially for experience below requirement
            ratio = resume_exp / required_exp
            return max(0, (ratio ** 0.5) * 100)
    
    def match_resume(self, resume_data: Dict, jd_text: str) -> Dict:
        """
        Calculate overall match score with explanation
        
        Returns:
            Dict with match score, matched skills, missing skills, and explanation
        """
        # Extract required skills from JD using a canonical skills list when available
        canonical_skills = resume_data.get('canonical_skills') or resume_data.get('skills')
        jd_skills = self.extract_skills_from_jd(jd_text, canonical_skills)
        
        # Calculate skill match
        skill_score, matched_skills, missing_skills = self.calculate_skill_match(
            resume_data['skills'], jd_skills
        )
        
        # Calculate TF-IDF similarity
        tfidf_score = self.calculate_tfidf_similarity(
            resume_data['full_text'], jd_text
        )
        
        # Calculate experience score
        exp_score = self.calculate_experience_score(
            resume_data['experience'], jd_text
        )
        
        # Weighted final score (skill match: 50%, TF-IDF: 30%, experience: 20%)
        final_score = (skill_score * 0.5) + (tfidf_score * 0.3) + (exp_score * 0.2)
        final_score = min(100, max(0, round(final_score, 2)))
        
        # Generate explanation
        explanation = self.generate_explanation(
            final_score, skill_score, tfidf_score, exp_score,
            matched_skills, missing_skills, resume_data['experience']
        )

        # Short explanation (2-3 lines) summarizing key factors
        short_explanation = self.generate_short_explanation(
            final_score, skill_score, tfidf_score, exp_score, matched_skills, missing_skills
        )
        
        return {
            "match_score": final_score,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "explanation": explanation,
            "short_explanation": short_explanation,
            "detailed_scores": {
                "skill_match": round(skill_score, 2),
                "tfidf_similarity": round(tfidf_score, 2),
                "experience_match": round(exp_score, 2)
            }
        }

    def generate_short_explanation(self, final_score, skill_score, tfidf_score, exp_score, matched_skills, missing_skills) -> str:
        """Create a concise 2-3 line explanation summarizing the scoring."""
        lines = []
        total_required = len(matched_skills) + len(missing_skills)
        matched_count = len(matched_skills)
        lines.append(f"Overall match: {final_score:.0f}% — Skills: {skill_score:.0f}% ({matched_count}/{total_required} matched)")
        lines.append(f"TF-IDF similarity: {tfidf_score:.0f}% · Experience score: {exp_score:.0f}%")
        if missing_skills:
            lines.append(f"Missing top skills: {', '.join(missing_skills[:3])}")
        return ' | '.join(lines[:3])
    
    def generate_explanation(self, final_score, skill_score, tfidf_score, 
                            exp_score, matched_skills, missing_skills, experience) -> str:
        """Generate a brief explanation of the match"""
        explanations = []
        
        # Skill match explanation
        if skill_score >= 80:
            explanations.append(f"Excellent skill match ({skill_score:.0f}%) with {len(matched_skills)} skills matched")
        elif skill_score >= 60:
            explanations.append(f"Good skill match ({skill_score:.0f}%) with {len(matched_skills)} skills matched")
        elif skill_score >= 40:
            explanations.append(f"Moderate skill match ({skill_score:.0f}%) with {len(matched_skills)} skills matched")
        else:
            explanations.append(f"Low skill match ({skill_score:.0f}%) - only {len(matched_skills)} skills matched")
        
        # Missing skills
        if missing_skills:
            explanations.append(f"Missing {len(missing_skills)} skills: {', '.join(missing_skills[:3])}")
            if len(missing_skills) > 3:
                explanations.append(f"and {len(missing_skills) - 3} more")
        else:
            explanations.append("All required skills matched!")
        
        # Experience match
        if experience:
            explanations.append(f"Experience: {experience:.1f} years ({exp_score:.0f}% match)")
        else:
            explanations.append("Experience not specified in resume")
        
        # Overall assessment
        if final_score >= 70:
            explanations.append("✅ Strong candidate match overall")
        elif final_score >= 50:
            explanations.append("📊 Moderate candidate match - consider for interview")
        else:
            explanations.append("⚠️ Low match - candidate may not be suitable")
        
        return " | ".join(explanations)