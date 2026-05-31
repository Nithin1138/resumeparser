# Resume Parser API

Parse PDF/DOCX resumes into structured JSON data. Built with FastAPI + spaCy.

## What it extracts
- Name, Email, Phone
- LinkedIn, GitHub URLs
- Skills (50+ tech keywords)
- Years of experience
- Sections: Summary, Experience, Education, Projects, Certifications

## Run locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

API docs at: http://localhost:8000/docs

## Deploy to Railway

1. Push this folder to GitHub
2. Go to railway.app → New Project → Deploy from GitHub
3. Select this repo → Railway auto-detects Procfile
4. Done — you get a live URL like https://yourapp.up.railway.app

## List on RapidAPI

1. Go to rapidapi.com/provider
2. Add New API → enter your Railway URL as Base URL
3. Add endpoint: POST /parse
4. Set pricing tiers:
   - Free: 10 calls/month
   - Basic ($9.99/mo): 500 calls/month
   - Pro ($29.99/mo): 5000 calls/month
   - Ultra ($99/mo): unlimited + batch endpoint

## Sample response

```json
{
  "success": true,
  "processing_time_seconds": 0.45,
  "filename": "john_resume.pdf",
  "data": {
    "name": "John Smith",
    "email": "john@gmail.com",
    "phone": "+91 98765 43210",
    "linkedin": "https://linkedin.com/in/johnsmith",
    "github": "https://github.com/johnsmith",
    "skills": ["python", "react", "docker", "aws", "sql"],
    "years_experience": 3,
    "sections": {
      "summary": "Software engineer with 3 years...",
      "experience": "Software Engineer at TCS...",
      "education": "B.Tech CSE, VIT University...",
      "projects": "Built a real-time chat app...",
      "certifications": "AWS Certified Developer..."
    },
    "raw_text_length": 3421
  }
}
```
# resumeparser
