# Career Navigator

An intelligent AI-powered career advisory platform that helps users navigate their professional journey through data-driven insights and personalized guidance.

## Features

- **Resume Analysis**: Upload your resume and get instant analysis of your skills and experience
- **Job Role Matching**: Get data-driven job role suggestions with match percentages based on your profile
- **Career Roadmap Generation**: Receive personalized learning paths and skill development recommendations
- **Skills Gap Analysis**: Identify missing skills required for your target role
- **Project Suggestions**: Get relevant project ideas to build your portfolio
- **Certification Recommendations**: Discover certifications that can boost your career prospects

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite for build tooling
- Material-UI (MUI) for UI components
- React Query for state management
- Axios for API calls

### Backend
- Python FastAPI
- scikit-learn for ML operations
- NLTK for text processing
- Krutrim Cloud AI for intelligent analysis
- MongoDB for data storage

## Prerequisites

Before you begin, ensure you have the following installed:
- Node.js (v18 or higher)
- Python (v3.12 or higher)
- MongoDB (v7.0 or higher)

## Local Development Setup

### Backend Setup

1. Navigate to the server directory:
   ```bash
   cd server
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the server directory with:
   ```
   MONGODB_URI=your_mongodb_uri
   KRUTRIM_CLOUD_API_KEY=your_krutrim_api_key
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The server will run on http://localhost:8000

### Frontend Setup

1. Navigate to the client directory:
   ```bash
   cd client
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the client directory with:
   ```
   VITE_API_URL=http://localhost:8000/api
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```
   The application will be available at http://localhost:5173

## API Documentation

Once the backend is running, you can access:
- API documentation: http://localhost:8000/docs
- API schemas: http://localhost:8000/openapi.json

## Running Tests

### Backend Tests
```bash
cd server
pytest
```

### Frontend Tests
```bash
cd client
npm test
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
