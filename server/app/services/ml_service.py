from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import numpy as np
import os
import logging
import json
from krutrim_cloud import KrutrimCloud
from dotenv import load_dotenv

# Set up logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables and log status
load_dotenv()
logger.info(f"Environment variables loaded. API Key present: {bool(os.getenv('KRUTRIM_CLOUD_API_KEY'))}")

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class MLService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
    
        # Initialize Krutrim client with better error handling
        api_key = os.getenv('KRUTRIM_CLOUD_API_KEY')
        if not api_key:
            logger.warning("KRUTRIM_CLOUD_API_KEY not found in environment variables")
            self.krutrim_client = None
        else:
            logger.info("Initializing Krutrim client with API key")
            try:
                self.krutrim_client = KrutrimCloud(api_key=api_key)
                logger.info("Krutrim client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Krutrim client: {str(e)}")
                self.krutrim_client = None
    
        self.model_name = "Krutrim-spectre-v2"

    def preprocess_text(self, text):
        # Tokenization
        tokens = word_tokenize(text.lower())
        # Remove stop words and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token.isalnum() and token not in self.stop_words]
        return " ".join(tokens)

    def extract_skills(self, text):
        # For now, using a simple keyword matching approach
        # In production, this should use a more sophisticated NER model
        common_skills = [
            "python", "java", "javascript", "react", "node.js", "sql",
            "machine learning", "data science", "cloud", "aws", "azure",
            "docker", "kubernetes", "ci/cd", "agile", "scrum"
        ]
        
        text_lower = text.lower()
        found_skills = [skill for skill in common_skills if skill in text_lower]
        return found_skills

    def get_job_recommendations(self, resume_text, job_descriptions):
        # Preprocess resume and job descriptions
        processed_resume = self.preprocess_text(resume_text)
        processed_jobs = [self.preprocess_text(job["description"]) for job in job_descriptions]
        
        # Create TF-IDF matrix
        all_texts = [processed_resume] + processed_jobs
        tfidf_matrix = self.vectorizer.fit_transform(all_texts)
        
        # Calculate similarity scores
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        # Get top matches
        top_indices = similarities[0].argsort()[::-1]
        
        recommendations = []
        for idx in top_indices:
            job = job_descriptions[idx]
            score = similarities[0][idx]
            recommendations.append({
                "job_id": str(job["_id"]),
                "title": job["title"],
                "company": job["company"],
                "score": float(score),
                "match_percentage": f"{score * 100:.1f}%"
            })
        
        return recommendations

    def get_fallback_roadmap(self, target_role, current_skills):
        """Generate a fallback roadmap when the API fails"""
        # Define common skills for different roles
        role_skills = {
            "Software Engineer": {
                "required": ["Python", "JavaScript", "SQL", "Git", "CI/CD"],
                "preferred": ["React", "Node.js", "Docker", "Cloud platforms"]
            },
            "Full Stack Developer": {
                "required": ["JavaScript", "HTML/CSS", "React", "Node.js", "SQL"],
                "preferred": ["TypeScript", "MongoDB", "AWS", "Docker"]
            },
            "ML Engineer": {
                "required": ["Python", "Machine Learning", "SQL", "Statistics"],
                "preferred": ["Deep Learning", "NLP", "MLOps", "Cloud ML"]
            },
            "Data Scientist": {
                "required": ["Python", "Statistics", "SQL", "Data Analysis"],
                "preferred": ["Machine Learning", "Data Visualization", "Big Data"]
            }
        }.get(target_role, {
            "required": ["Programming", "Problem Solving", "Version Control"],
            "preferred": ["Cloud Computing", "Agile Methodologies"]
        })

        # Calculate skills gap
        current_skills_set = set(skill.lower() for skill in current_skills)
        missing_required = [
            f"Required: {skill}" 
            for skill in role_skills["required"] 
            if skill.lower() not in current_skills_set
        ]
        missing_preferred = [
            f"Preferred: {skill}" 
            for skill in role_skills["preferred"] 
            if skill.lower() not in current_skills_set
        ]

        return {
            "skills_gap": missing_required + missing_preferred,
            "learning_path": [
                {
                    "title": "Master Core Skills",
                    "duration": "1-2 months",
                    "tasks": [
                        f"Complete online courses in {skill}" 
                        for skill in role_skills["required"][:3]
                    ]
                },
                {
                    "title": "Build Practical Experience",
                    "duration": "2-3 months",
                    "tasks": [
                        "Work on personal projects",
                        "Contribute to open source",
                        "Build portfolio projects"
                    ]
                }
            ],
            "certifications": [
                "AWS Certified Developer",
                "Professional Scrum Developer",
                "Role-specific technical certification"
            ],
            "projects": [
                {
                    "title": f"{target_role} Portfolio Project",
                    "description": f"Build a comprehensive project showcasing key {target_role} skills"
                },
                {
                    "title": "Open Source Contribution",
                    "description": "Contribute to relevant open source projects in your domain"
                }
            ]
        }

    async def get_career_roadmap(self, resume_text, target_role):
        if not self.krutrim_client:
            logger.warning("Krutrim client not initialized, using fallback roadmap")
            current_skills = self.extract_skills(resume_text)
            return self.get_fallback_roadmap(target_role, current_skills)

        try:
            # Extract current skills from resume
            current_skills = self.extract_skills(resume_text)
            skills_text = ", ".join(current_skills) if current_skills else "No specific skills detected"
            
            logger.info(f"Generating roadmap for role: {target_role}")
            logger.info(f"Detected skills: {skills_text}")

            system_prompt = """You are a career development expert AI. 
            You must respond with a valid JSON object containing exactly these keys(only JSON format):
            "skills_gap", "learning_path", "certifications", "projects".
            Important: All string values must be properly quoted. Duration values in learning_path must be strings (e.g. "6 months" not 6 months).
            Do not include any explanation or text outside the JSON structure."""

            user_prompt = f"""Create a detailed career roadmap based on this information:
            
            Resume Skills: {skills_text}
            Target Role: {target_role}
            Resume Context: {resume_text[:1000]}...

            Respond with a JSON object containing:

            1. "skills_gap": Array of strings, each prefixed with either "Required: " or "Preferred: "
               Example: ["Required: Python", "Preferred: Docker"]

            2. "learning_path": Array of objects, each with:
               - "title": phase name (string)
               - "duration": time period (string, e.g., "6 months" or "12 weeks")
               - "tasks": array of specific tasks (strings)

            3. "certifications": Array of certification names (strings)

            4. "projects": Array of objects, each with:
               - "title": project name (string)
               - "description": detailed description (string)
            """

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            logger.info("Sending request to Krutrim API...")
            
            response = self.krutrim_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=False,
                temperature=0.7,
                max_tokens=2000
            )

            logger.info("Successfully received response from Krutrim API")
            
            # Debug the raw response
            logger.info(f"Raw API response type: {type(response)}")
            logger.info(f"Raw API response: {response}")
            
            try:
                # Check if response has the expected structure
                if not hasattr(response, 'choices') or not response.choices:
                    logger.error("Invalid response structure: missing choices")
                    return self.get_fallback_roadmap(target_role, current_skills)
                    
                complete_response = response.choices[0].message.content
                logger.info(f"Response content: {complete_response}")
                
                # Try to parse the JSON content
                try:
                    roadmap_data = json.loads(complete_response)
                except json.JSONDecodeError as je:
                    logger.error(f"JSON parsing error: {str(je)}")
                    logger.error(f"Failed content: {complete_response}")
                    return self.get_fallback_roadmap(target_role, current_skills)

                # Validate the roadmap data structure
                required_keys = ["skills_gap", "learning_path", "certifications", "projects"]
                if not all(key in roadmap_data for key in required_keys):
                    logger.error(f"Missing required keys. Got keys: {list(roadmap_data.keys())}")
                    return self.get_fallback_roadmap(target_role, current_skills)
                
                return roadmap_data

            except AttributeError as ae:
                logger.error(f"Failed to access response attributes: {str(ae)}")
                return self.get_fallback_roadmap(target_role, current_skills)

        except Exception as e:
            logger.error(f"Error in career roadmap generation: {str(e)}", exc_info=True)
            return self.get_fallback_roadmap(target_role, current_skills)