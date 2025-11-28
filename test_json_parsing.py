#!/usr/bin/env python3
"""
Test script to verify JSON parsing fixes for the Krutrim API response
"""
import json
import re

def clean_json_response(json_string):
    """Clean up JSON response from Krutrim API to remove trailing commas and other issues"""
    try:
        # Remove trailing commas before closing brackets/braces
        json_string = re.sub(r',(\s*[}\]])', r'\1', json_string)
        
        # Remove any extra spaces around colons and commas
        json_string = re.sub(r'\s*:\s*', ':', json_string)
        json_string = re.sub(r'\s*,\s*', ',', json_string)
        
        # Ensure proper quotes around property names
        json_string = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_string)
        
        # Remove any trailing commas that might still exist
        json_string = re.sub(r',(\s*[}\]])', r'\1', json_string)
        
        return json_string
    except Exception as e:
        print(f"Error cleaning JSON: {str(e)}")
        return json_string

# Test with the actual problematic JSON from the logs
problematic_json = """{
    "skills_gap": [
        "Required: Python",
        "Preferred: Docker"
    ],
    "learning_path": [
        {
            "title": "Full Stack Development",
            "duration": "1 year",
            "tasks": ["HTML", "CSS", "JavaScript", "React", "Node.js", "MongoDB", "Express", "Git", "CI/CD"],
        },
        {
            "title": "Data Science Fundamentals",
            "duration": "3 months",
            "tasks": ["Python", "Numpy", "Pandas", "Scipy", "matplotlib", "Seaborn", "Tensorflow", "Keras", "NLTK", "NLP", "Statistics", "Data Visualization"],
        },
        {
            "title": "Advanced Machine Learning Techniques",
            "duration": "6 months",
            "tasks": ["Scikit-learn", "XGBoost", "random forest", "gradient boosting", "neural networks", "deep learning", "natural language processing", "reinforcement learning", "clustering algorithms", "decision trees", "ensemble methods"],
        },
    ],
    "certifications": [
        "Data Science Certification Training",
        "Python Certification Training",
        "Machine Learning Certification Training",
        "Deep Learning Specialization",
        "Neural Networks and Deep Learning",
        "Advanced Programming with Python",
        "Cloud Computing Certification Training"
    ],
    "projects": [
        {
            "title": "Weather Forecasting Model",
            "description": "Used Linear Regression and Random Forest techniques to build a forecasting model that predicts weather conditions for the next day."
        },
        {
            "title": "Sentiment Analysis Project",
            "description": "Analyzed thousands of tweets from various topics to identify positive and negative sentiments towards brands and products."
        },
        {
            "title": "Recommendation System",
            "description": "Used Collaborative Filtering algorithm to recommend movies to users based on their viewing history."
        }
    ]
}"""

print("=== Testing JSON Parsing Fix ===")
print("\n1. Original problematic JSON:")
print(problematic_json[:200] + "...")

print("\n2. Attempting to parse original JSON:")
try:
    original_parsed = json.loads(problematic_json)
    print("✅ Original JSON parsed successfully!")
except json.JSONDecodeError as e:
    print(f"❌ Original JSON parsing failed: {e}")

print("\n3. Cleaning JSON and attempting to parse:")
cleaned_json = clean_json_response(problematic_json)
print("Cleaned JSON:")
print(cleaned_json[:200] + "...")

try:
    cleaned_parsed = json.loads(cleaned_json)
    print("✅ Cleaned JSON parsed successfully!")
    
    # Validate structure
    required_keys = ["skills_gap", "learning_path", "certifications", "projects"]
    if all(key in cleaned_parsed for key in required_keys):
        print("✅ All required keys present")
        print(f"   - Skills gap: {len(cleaned_parsed['skills_gap'])} items")
        print(f"   - Learning path: {len(cleaned_parsed['learning_path'])} phases")
        print(f"   - Certifications: {len(cleaned_parsed['certifications'])} items")
        print(f"   - Projects: {len(cleaned_parsed['projects'])} items")
    else:
        print("❌ Missing required keys")
        
except json.JSONDecodeError as e:
    print(f"❌ Cleaned JSON parsing still failed: {e}")

print("\n=== Test Complete ===")