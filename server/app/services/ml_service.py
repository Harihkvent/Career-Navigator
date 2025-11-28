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
import re
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

    def clean_json_response(self, json_string):
        """Clean up JSON response from Krutrim API to remove trailing commas and other issues"""
        try:
            # Remove trailing commas before closing brackets and braces
            # This regex matches a comma followed by optional whitespace and then a closing bracket/brace
            json_string = re.sub(r',(\s*[}\]])', r'\1', json_string)
            
            # Handle multiple trailing commas that might exist
            json_string = re.sub(r',+(\s*[}\]])', r'\1', json_string)
            
            # Remove any leading/trailing whitespace
            json_string = json_string.strip()
            
            return json_string
        except Exception as e:
            logger.error(f"Error cleaning JSON: {str(e)}")
            return json_string

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
        """Generate a comprehensive fallback roadmap when the API fails"""
        # Define detailed skills and roadmaps for different roles
        role_data = {
            "Software Engineer": {
                "required": ["Python", "JavaScript", "SQL", "Git", "System Design"],
                "preferred": ["React", "Node.js", "Docker", "AWS", "Kubernetes"],
                "learning_phases": [
                    {
                        "title": "Foundation Programming Skills",
                        "duration": "2-3 months",
                        "tasks": [
                            "Master Python fundamentals and OOP concepts",
                            "Learn JavaScript ES6+ and async programming",
                            "Practice data structures and algorithms daily",
                            "Complete SQL queries and database design course",
                            "Set up Git workflow and version control best practices"
                        ]
                    },
                    {
                        "title": "Web Development & Frameworks",
                        "duration": "3-4 months", 
                        "tasks": [
                            "Build REST APIs with Express.js or FastAPI",
                            "Create responsive UIs with React and modern CSS",
                            "Learn state management with Redux or Context API",
                            "Implement authentication and authorization systems",
                            "Practice test-driven development with Jest/PyTest"
                        ]
                    },
                    {
                        "title": "DevOps & Cloud Deployment",
                        "duration": "2-3 months",
                        "tasks": [
                            "Containerize applications with Docker and docker-compose",
                            "Deploy applications to AWS EC2, Lambda, and RDS",
                            "Set up CI/CD pipelines with GitHub Actions",
                            "Monitor applications with logging and metrics",
                            "Practice system design for scalable architectures"
                        ]
                    }
                ],
                "certifications": ["AWS Certified Developer Associate", "Microsoft Azure Developer Associate", "Google Cloud Professional Developer"],
                "projects": [
                    {
                        "title": "E-commerce Platform with Microservices",
                        "description": "Build a full-stack e-commerce platform using React frontend, Node.js/Express backend with microservices architecture, PostgreSQL database, Redis caching, and deploy on AWS with Docker containers."
                    },
                    {
                        "title": "Real-time Chat Application", 
                        "description": "Develop a real-time messaging app with WebSocket connections, user authentication, message persistence, file uploads, and responsive design using React and Socket.io."
                    },
                    {
                        "title": "Task Management API with Analytics",
                        "description": "Create a RESTful API for task management with user roles, data analytics dashboard, automated testing, API documentation, and CI/CD deployment pipeline."
                    }
                ]
            },
            "Full Stack Developer": {
                "required": ["JavaScript", "HTML/CSS", "React", "Node.js", "Databases"],
                "preferred": ["TypeScript", "MongoDB", "AWS", "Docker", "GraphQL"],
                "learning_phases": [
                    {
                        "title": "Frontend Mastery",
                        "duration": "2-3 months",
                        "tasks": [
                            "Master modern JavaScript ES6+ features and async/await",
                            "Build responsive layouts with CSS Grid and Flexbox",
                            "Learn React hooks, context, and component lifecycle",
                            "Implement state management with Redux Toolkit",
                            "Practice TypeScript for type-safe development"
                        ]
                    },
                    {
                        "title": "Backend Development",
                        "duration": "3-4 months",
                        "tasks": [
                            "Build RESTful APIs with Node.js and Express",
                            "Design database schemas with PostgreSQL and MongoDB",
                            "Implement JWT authentication and authorization",
                            "Create GraphQL APIs for efficient data fetching",
                            "Write comprehensive API tests with Supertest"
                        ]
                    },
                    {
                        "title": "Full Stack Integration",
                        "duration": "2-3 months", 
                        "tasks": [
                            "Deploy full-stack applications to Vercel and Heroku",
                            "Implement real-time features with WebSockets",
                            "Set up monitoring with error tracking and analytics",
                            "Optimize performance with caching and lazy loading",
                            "Create mobile-responsive progressive web apps"
                        ]
                    }
                ],
                "certifications": ["Meta Frontend Developer Certificate", "MongoDB Developer Path", "AWS Certified Cloud Practitioner"],
                "projects": [
                    {
                        "title": "Social Media Dashboard with Analytics",
                        "description": "Build a full-stack social media management platform with React/Next.js frontend, Node.js backend, MongoDB database, real-time notifications, data visualization charts, and third-party API integrations."
                    },
                    {
                        "title": "Collaborative Project Management Tool",
                        "description": "Develop a team collaboration platform similar to Trello with drag-and-drop functionality, real-time updates, file attachments, user roles, and mobile-responsive design using MERN stack."
                    },
                    {
                        "title": "E-learning Platform with Video Streaming",
                        "description": "Create an online learning platform with video streaming, progress tracking, quiz system, payment integration, instructor dashboard, and student analytics using React, Node.js, and AWS services."
                    }
                ]
            },
            "ML Engineer": {
                "required": ["Python", "Machine Learning", "Statistics", "Data Processing", "MLOps"],
                "preferred": ["TensorFlow", "PyTorch", "AWS SageMaker", "Docker", "Kubernetes"],
                "learning_phases": [
                    {
                        "title": "ML Fundamentals & Statistics", 
                        "duration": "3-4 months",
                        "tasks": [
                            "Master Python for data science with NumPy, Pandas, Matplotlib",
                            "Learn statistics, probability, and hypothesis testing",
                            "Implement ML algorithms from scratch (linear regression, decision trees)",
                            "Practice feature engineering and data preprocessing techniques",
                            "Complete Scikit-learn for classical machine learning models"
                        ]
                    },
                    {
                        "title": "Deep Learning & Advanced ML",
                        "duration": "4-5 months",
                        "tasks": [
                            "Learn neural networks and deep learning with TensorFlow/PyTorch",
                            "Implement CNNs for computer vision tasks",
                            "Build RNNs and Transformers for NLP applications",
                            "Practice model optimization and hyperparameter tuning",
                            "Study reinforcement learning and generative models"
                        ]
                    },
                    {
                        "title": "MLOps & Production Systems",
                        "duration": "3-4 months",
                        "tasks": [
                            "Deploy ML models using Flask/FastAPI and Docker containers",
                            "Set up ML pipelines with Apache Airflow or Kubeflow",
                            "Implement model monitoring and A/B testing frameworks",
                            "Use cloud ML services (AWS SageMaker, Google AI Platform)",
                            "Practice model versioning with MLflow and DVC"
                        ]
                    }
                ],
                "certifications": ["Google Cloud Professional ML Engineer", "AWS Certified Machine Learning Specialty", "TensorFlow Developer Certificate"],
                "projects": [
                    {
                        "title": "Computer Vision System for Object Detection",
                        "description": "Build an end-to-end computer vision pipeline using YOLOv8 or ResNet for real-time object detection, deployed as a REST API with Flask, containerized with Docker, and hosted on AWS with model monitoring."
                    },
                    {
                        "title": "NLP Sentiment Analysis Platform",
                        "description": "Develop a sentiment analysis system using BERT or GPT models, with data preprocessing pipeline, model fine-tuning, web interface, and real-time prediction API deployed on cloud infrastructure."
                    },
                    {
                        "title": "Recommendation Engine with MLOps",
                        "description": "Create a scalable recommendation system using collaborative filtering and deep learning, with automated ML pipeline, A/B testing framework, model monitoring, and continuous deployment using Kubernetes."
                    }
                ]
            },
            "Data Scientist": {
                "required": ["Python", "Statistics", "SQL", "Data Analysis", "Machine Learning"],
                "preferred": ["R", "Tableau", "Spark", "Cloud Platforms", "Deep Learning"],
                "learning_phases": [
                    {
                        "title": "Data Analysis Foundation",
                        "duration": "2-3 months",
                        "tasks": [
                            "Master Python data science stack (Pandas, NumPy, Matplotlib, Seaborn)",
                            "Learn advanced SQL for complex queries and window functions", 
                            "Practice statistical analysis and hypothesis testing",
                            "Create interactive data visualizations with Plotly and Dash",
                            "Study experimental design and A/B testing methodologies"
                        ]
                    },
                    {
                        "title": "Machine Learning & Modeling",
                        "duration": "3-4 months",
                        "tasks": [
                            "Implement supervised and unsupervised learning algorithms",
                            "Practice feature engineering and model selection techniques",
                            "Learn ensemble methods and model interpretability (SHAP, LIME)",
                            "Build time series forecasting models with Prophet and ARIMA",
                            "Study deep learning for structured and unstructured data"
                        ]
                    },
                    {
                        "title": "Big Data & Production Systems",
                        "duration": "3-4 months",
                        "tasks": [
                            "Process large datasets with Apache Spark and Dask",
                            "Build automated data pipelines with Apache Airflow",
                            "Deploy models as web services with Flask and Streamlit",
                            "Use cloud data platforms (AWS Redshift, Google BigQuery)",
                            "Implement data quality monitoring and model governance"
                        ]
                    }
                ],
                "certifications": ["Google Data Analytics Professional Certificate", "Microsoft Azure Data Scientist Associate", "Cloudera Data Analyst"],
                "projects": [
                    {
                        "title": "Customer Segmentation & Lifetime Value Analysis",
                        "description": "Perform comprehensive customer analytics using RFM analysis, clustering algorithms, and predictive modeling to segment customers and predict lifetime value, with interactive dashboard built in Streamlit."
                    },
                    {
                        "title": "Time Series Forecasting for Sales Prediction", 
                        "description": "Build advanced forecasting models using Prophet, ARIMA, and LSTM networks to predict sales trends, incorporating external factors like seasonality and promotions, deployed as automated reporting system."
                    },
                    {
                        "title": "Marketing Attribution & A/B Testing Platform",
                        "description": "Develop a data science platform for marketing attribution analysis, multi-touch attribution modeling, A/B test design and analysis, with statistical significance testing and automated reporting dashboard."
                    }
                ]
            }
        }.get(target_role, {
            "required": ["Programming", "Problem Solving", "Version Control"],
            "preferred": ["Cloud Computing", "Agile Methodologies"],
            "learning_phases": [
                {
                    "title": "Technical Foundation",
                    "duration": "2-3 months", 
                    "tasks": ["Learn core programming concepts", "Practice problem-solving skills", "Master version control with Git"]
                },
                {
                    "title": "Specialized Skills",
                    "duration": "3-4 months",
                    "tasks": ["Develop role-specific technical skills", "Build portfolio projects", "Contribute to open source"]
                }
            ],
            "certifications": ["CompTIA IT Fundamentals", "AWS Cloud Practitioner"],
            "projects": [
                {
                    "title": "Personal Portfolio Website",
                    "description": "Create a professional portfolio showcasing your skills and projects"
                }
            ]
        })

        # Calculate skills gap
        current_skills_set = set(skill.lower().strip() for skill in current_skills)
        missing_required = [
            f"Required: {skill}" 
            for skill in role_data["required"] 
            if skill.lower().strip() not in current_skills_set
        ]
        missing_preferred = [
            f"Preferred: {skill}" 
            for skill in role_data["preferred"] 
            if skill.lower().strip() not in current_skills_set
        ]

        return {
            "skills_gap": missing_required + missing_preferred,
            "learning_path": role_data["learning_phases"],
            "certifications": role_data["certifications"],
            "projects": role_data["projects"]
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

            system_prompt = """You are a senior career development expert and technical mentor with deep industry experience. 
            You analyze resumes and create personalized, actionable career roadmaps for tech professionals.
            
            You MUST respond with ONLY a valid JSON object containing exactly these keys:
            "skills_gap", "learning_path", "certifications", "projects".
            
            CRITICAL JSON FORMATTING RULES:
            - NO trailing commas anywhere in the JSON
            - All property names must be in double quotes
            - All string values must be in double quotes
            - Duration values must be strings (e.g. "6 months" not 6 months)
            - Do not include any text or explanation outside the JSON structure
            - Ensure the JSON is syntactically correct and parseable
            
            CONTENT REQUIREMENTS:
            - Provide SPECIFIC, REAL skills, technologies, and certifications
            - Create ACTIONABLE learning tasks with real course names, technologies, and frameworks
            - Suggest ACTUAL certifications that exist in the industry
            - Design REALISTIC projects with clear technical descriptions
            - Match everything to the specific target role and current skill level"""

            user_prompt = f"""Analyze this professional profile and create a comprehensive career roadmap for becoming a {target_role}:

            CURRENT SKILLS: {skills_text}
            TARGET ROLE: {target_role}
            RESUME CONTEXT: {resume_text[:1000]}...

            Based on this analysis, create a detailed roadmap with:

            1. SKILLS GAP: Identify specific missing technical skills required for {target_role}
               - Mark as "Required:" for essential skills
               - Mark as "Preferred:" for nice-to-have skills
               - Include specific technologies, frameworks, tools, and methodologies

            2. LEARNING PATH: Design 3-4 progressive learning phases
               - Each phase should have realistic duration (2-6 months)
               - Include 4-6 specific, actionable learning tasks per phase
               - Mention real courses, platforms, technologies, and hands-on activities
               - Progress from foundational to advanced concepts

            3. CERTIFICATIONS: Recommend actual industry certifications
               - Include vendor-specific certs (AWS, Microsoft, Google, etc.)
               - Professional certifications relevant to {target_role}
               - Industry-recognized credentials

            4. PROJECTS: Suggest 3-4 portfolio projects
               - Each project should demonstrate key {target_role} skills
               - Include specific technical stack and implementation details
               - Projects should increase in complexity and scope

            Respond with ONLY a valid JSON object (no other text). Use actual technology names, real certification titles, specific course names, and concrete project ideas that would impress hiring managers for {target_role} positions.

            JSON Format (NO trailing commas):
            {{
              "skills_gap": ["Required: Specific Technology", "Preferred: Specific Framework"],
              "learning_path": [
                {{
                  "title": "Descriptive Phase Name", 
                  "duration": "X months",
                  "tasks": ["Specific learning task with real technologies", "Another concrete task"]
                }}
              ],
              "certifications": ["Real Certification Name", "Another Real Cert"],
              "projects": [
                {{
                  "title": "Specific Project Name",
                  "description": "Detailed technical description with tech stack and implementation approach"
                }}
              ]
            }}"""

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
                
                # Clean and parse the JSON content
                try:
                    # First attempt - try to parse as is
                    roadmap_data = json.loads(complete_response)
                except json.JSONDecodeError as je:
                    logger.warning(f"Initial JSON parsing failed: {str(je)}")
                    logger.info("Attempting to clean JSON response...")
                    
                    try:
                        # Clean the JSON and try again
                        cleaned_response = self.clean_json_response(complete_response)
                        logger.info(f"Cleaned content: {cleaned_response}")
                        roadmap_data = json.loads(cleaned_response)
                    except json.JSONDecodeError as je2:
                        logger.error(f"JSON parsing error after cleanup: {str(je2)}")
                        logger.error(f"Failed content: {complete_response}")
                        logger.error(f"Cleaned content: {cleaned_response}")
                        return self.get_fallback_roadmap(target_role, current_skills)

                # Validate the roadmap data structure
                required_keys = ["skills_gap", "learning_path", "certifications", "projects"]
                if not all(key in roadmap_data for key in required_keys):
                    logger.error(f"Missing required keys. Expected: {required_keys}, Got: {list(roadmap_data.keys())}")
                    return self.get_fallback_roadmap(target_role, current_skills)
                
                # Validate data types
                if not isinstance(roadmap_data["skills_gap"], list):
                    logger.error("skills_gap is not a list")
                    return self.get_fallback_roadmap(target_role, current_skills)
                
                if not isinstance(roadmap_data["learning_path"], list):
                    logger.error("learning_path is not a list")
                    return self.get_fallback_roadmap(target_role, current_skills)
                
                logger.info(f"Successfully parsed roadmap with {len(roadmap_data['skills_gap'])} skills gaps, {len(roadmap_data['learning_path'])} learning phases, {len(roadmap_data['certifications'])} certifications, {len(roadmap_data['projects'])} projects")
                
                return roadmap_data

            except AttributeError as ae:
                logger.error(f"Failed to access response attributes: {str(ae)}")
                return self.get_fallback_roadmap(target_role, current_skills)

        except Exception as e:
            logger.error(f"Error in career roadmap generation: {str(e)}", exc_info=True)
            logger.info("Falling back to default roadmap generation")
            fallback_roadmap = self.get_fallback_roadmap(target_role, current_skills)
            logger.info(f"Generated fallback roadmap with {len(fallback_roadmap['skills_gap'])} skills gaps")
            return fallback_roadmap