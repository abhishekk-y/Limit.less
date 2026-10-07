"""Small curated DEMO taxonomy and fictional opportunities. No live-market claims."""

from copy import deepcopy

SKILLS = [
    ("python", "Python", [], 12),
    ("sql", "SQL", [], 10),
    ("git", "Git", [], 6),
    ("linux", "Linux", [], 8),
    ("docker", "Docker", ["linux"], 12),
    ("aws", "AWS", ["linux"], 20),
    ("kubernetes", "Kubernetes", ["docker"], 20),
    ("javascript", "JavaScript", [], 16),
    ("typescript", "TypeScript", ["javascript"], 10),
    ("react", "React", ["javascript"], 18),
    ("html", "HTML", [], 6),
    ("css", "CSS", ["html"], 8),
    ("machine_learning", "Machine Learning", ["python"], 24),
    ("pandas", "Pandas", ["python"], 8),
    ("statistics", "Statistics", [], 18),
    ("fastapi", "FastAPI", ["python"], 10),
    ("testing", "Testing", [], 8),
    ("communication", "Communication", [], 6),
    ("agile", "Agile", [], 6),
    ("figma", "Figma", [], 10),
    ("excel", "Excel", [], 8),
    ("power_bi", "Power BI", ["excel"], 12),
    ("cybersecurity", "Cybersecurity", ["linux"], 20),
    ("networking", "Networking", [], 12),
    ("sas_foundations", "SAS Foundations", [], 8),
]
TAXONOMY = {
    key: {
        "id": key,
        "name": name,
        "prerequisites": prereqs,
        "hours": hours,
        "is_demo": True,
        "version": "demo-v1",
    }
    for key, name, prereqs, hours in SKILLS
}
ROLES = [
    {
        "id": "software-engineer",
        "title": "Software Engineer",
        "skills": ["python", "sql", "git", "testing", "fastapi"],
    },
    {
        "id": "data-scientist",
        "title": "Data Scientist",
        "skills": ["python", "sql", "machine_learning", "pandas", "statistics"],
    },
    {
        "id": "frontend-engineer",
        "title": "Frontend Engineer",
        "skills": ["html", "css", "javascript", "typescript", "react"],
    },
    {
        "id": "cloud-engineer",
        "title": "Cloud Engineer",
        "skills": ["linux", "docker", "aws", "kubernetes", "git"],
    },
    {
        "id": "data-analyst",
        "title": "Data Analyst",
        "skills": ["sql", "excel", "power_bi", "statistics", "communication"],
    },
    {
        "id": "security-analyst",
        "title": "Security Analyst",
        "skills": ["linux", "networking", "cybersecurity", "python"],
    },
]
TYPES = [
    "private",
    "internship",
    "apprenticeship",
    "scholarship",
    "fellowship",
    "hackathon",
    "research",
    "freelance",
]


def opportunities():
    result = []
    for index in range(96):
        role = ROLES[index % len(ROLES)]
        kind = TYPES[(index // len(ROLES)) % len(TYPES)]
        result.append(
            {
                "id": f"demo-{index + 1:03}",
                "title": f"{role['title']} · {kind.title()}",
                "organization": f"Demo Organization {index % 12 + 1}",
                "role_id": role["id"],
                "type": kind,
                "location": ["Bengaluru", "Delhi", "Pune", "Indore", "Remote"][index % 5],
                "skills": role["skills"][: 3 + index % 3],
                "is_demo": True,
                "description": "Fictional opportunity for testing the career workflow. No real vacancy or submission.",
                "requirements": {"min_age": 18} if kind == "apprenticeship" else {},
                "source": "SkillSetu fictional demo catalog v1",
                "deadline": None,
            }
        )
    return result


def get_opportunity(opportunity_id):
    return next((deepcopy(item) for item in opportunities() if item["id"] == opportunity_id), None)
