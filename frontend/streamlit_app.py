import streamlit as st
import requests
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Smart Resume Screening System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .score-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .skill-tag {
        background-color: #e1f5fe;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        display: inline-block;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    .missing-skill-tag {
        background-color: #ffebee;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        display: inline-block;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #155a8a;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">📄 Smart Resume Screening System</h1>', unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.1rem; color: #666;">
            AI-powered resume screening using TF-IDF and skill-based matching
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    # API Configuration
    api_url = st.text_input(
        "API Endpoint",
        value="http://localhost:8000",
        help="URL of the FastAPI backend"
    )
    
    st.markdown("---")
    st.markdown("### 📊 About")
    st.markdown("""
    This system uses:
    - **TF-IDF** for text similarity
    - **Skill matching** for keyword analysis
    - **Experience matching** for years of experience
    
    **Weights:**
    - Skills: 50%
    - TF-IDF: 30%
    - Experience: 20%
    """)
    
    st.markdown("---")
    st.markdown("### 🚀 Quick Tips")
    st.markdown("""
    1. Upload a PDF resume
    2. Paste the job description
    3. Click 'Analyze Resume'
    4. Review the detailed results
    """)

# Main content - Two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📤 Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload resume in PDF format"
    )
    
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        st.info(f"📄 File size: {uploaded_file.size / 1024:.1f} KB")
    
    st.markdown("### 📝 Job Description")
    job_description = st.text_area(
        "Enter the job description",
        height=200,
        placeholder="Paste the job description here...",
        help="Include skills, experience requirements, and responsibilities"
    )
    
    # Sample JD button
    if st.button("📋 Load Sample Job Description"):
        sample_jd = """We are looking for a Senior Python Developer with 5+ years of experience.
        
        Required Skills:
        - Python
        - Django
        - React
        - PostgreSQL
        - AWS
        - Docker
        - REST APIs
        
        Nice to have:
        - Machine Learning
        - Kubernetes
        - Microservices
        
        Responsibilities:
        - Design and develop scalable web applications
        - Lead technical decisions
        - Mentor junior developers
        """
        job_description = sample_jd
        st.rerun()

with col2:
    st.markdown("### 🔍 Analysis Results")
    
    # Analyze button
    analyze_button = st.button("🚀 Analyze Resume", use_container_width=True)
    
    if analyze_button:
        if not uploaded_file:
            st.error("⚠️ Please upload a resume PDF file")
        elif not job_description:
            st.error("⚠️ Please enter a job description")
        else:
            # Show loading spinner
            with st.spinner("🔄 Analyzing resume against job description..."):
                try:
                    # Prepare files and data for API request
                    files = {
                        'resume_file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')
                    }
                    data = {
                        'job_description': job_description
                    }
                    
                    # Make API request
                    response = requests.post(
                        f"{api_url}/match",
                        files=files,
                        data=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display results
                        st.success("✅ Analysis Complete!")

                        # Short explanation (2-3 line summary) from backend
                        short_expl = result.get('short_explanation')
                        if short_expl:
                            st.markdown(f"""
                            <div class="score-box">
                                <strong>Summary:</strong>
                                <p style="font-size:1.05rem; margin:0.25rem 0;">{short_expl}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Match Score with gauge
                        score = result['match_score']
                        score_color = "green" if score >= 70 else "orange" if score >= 50 else "red"
                        
                        # Score display
                        col_score1, col_score2, col_score3 = st.columns(3)
                        with col_score1:
                            st.metric(
                                label="🎯 Match Score",
                                value=f"{score:.1f}%",
                                delta=None
                            )
                        with col_score2:
                            st.metric(
                                label="✅ Matched Skills",
                                value=len(result['matched_skills'])
                            )
                        with col_score3:
                            st.metric(
                                label="❌ Missing Skills",
                                value=len(result['missing_skills'])
                            )
                        
                        # Detailed scores
                        st.markdown("### 📊 Detailed Scores")
                        col_d1, col_d2, col_d3 = st.columns(3)
                        with col_d1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🎯 Skill Match</h4>
                                <h2>{result['detailed_scores']['skill_match']:.1f}%</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        with col_d2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>📝 TF-IDF Similarity</h4>
                                <h2>{result['detailed_scores']['tfidf_similarity']:.1f}%</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        with col_d3:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>💼 Experience Match</h4>
                                <h2>{result['detailed_scores']['experience_match']:.1f}%</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Skills section
                        st.markdown("### 🛠️ Skills Analysis")
                        
                        col_skills1, col_skills2 = st.columns(2)
                        
                        with col_skills1:
                            st.markdown("#### ✅ Matched Skills")
                            if result['matched_skills']:
                                skills_html = "".join([
                                    f'<span class="skill-tag">{skill}</span> ' 
                                    for skill in result['matched_skills']
                                ])
                                st.markdown(skills_html, unsafe_allow_html=True)
                            else:
                                st.warning("No matching skills found")
                        
                        with col_skills2:
                            st.markdown("#### ❌ Missing Skills")
                            if result['missing_skills']:
                                skills_html = "".join([
                                    f'<span class="missing-skill-tag">{skill}</span> ' 
                                    for skill in result['missing_skills']
                                ])
                                st.markdown(skills_html, unsafe_allow_html=True)
                            else:
                                st.success("All required skills matched! 🎉")
                        
                        # Explanation
                        st.markdown("### 💡 Explanation")
                        st.markdown(f"""
                        <div class="score-box">
                            <p style="font-size: 1.1rem;">{result['explanation']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Resume metadata
                        with st.expander("📋 Resume Metadata"):
                            metadata = result['resume_metadata']
                            st.json({
                                "filename": metadata['filename'],
                                "skills_found": metadata['skills_found'],
                                "experience_years": metadata['experience_years'],
                                "all_skills": metadata['all_skills'][:10]  # Show first 10 skills
                            })
                        
                        # Recommendation
                        st.markdown("### 🎯 Recommendation")
                        if score >= 70:
                            st.success("✅ **Strong Candidate** - This resume is a good match! Consider scheduling an interview.")
                        elif score >= 50:
                            st.warning("📊 **Moderate Candidate** - Consider for interview but review missing skills.")
                        else:
                            st.error("⚠️ **Low Match** - Candidate may not be suitable for this role.")
                        
                    else:
                        st.error(f"❌ Error: {response.status_code} - {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on localhost:8000")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
    else:
        st.info("👆 Upload a resume and enter a job description, then click 'Analyze Resume'")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    Built with ❤️ using FastAPI and Streamlit | Smart Resume Screening System v1.0
</div>
""", unsafe_allow_html=True)