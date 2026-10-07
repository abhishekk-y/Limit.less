# API Reference

## Base URL
`/api/v1`

## Endpoints

### 1. Extraction
- **POST** `/extract`
  - Body: `{"text": "resume content"}`
  - Response: `{"skills": [...], "education": [...]}`

### 2. Matching
- **POST** `/match`
  - Body: `{"candidate_id": "...", "job_id": "..."}`
  - Response: `{"match_score": 85.5, "cds": 15, "sts": 0.8}`

### 3. Career GPS
- **GET** `/career-gps/{candidate_id}`
  - Response: `{"path": ["Python", "ML", "Deep Learning"]}`
