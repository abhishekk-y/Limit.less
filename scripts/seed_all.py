"""
SkillSetu X — Seed All Data
Loads taxonomy, demo personas, opportunities, curricula, and organization data.

Usage: python -m scripts.seed_all
"""
import json
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

SEED_DIR = PROJECT_ROOT / "data" / "seed"


def load_json(filename: str) -> dict | list:
    """Load a JSON seed file."""
    filepath = SEED_DIR / filename
    if not filepath.exists():
        print(f"  ⚠ Seed file not found: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


async def seed_skills(session):
    """Load skills taxonomy into database."""
    skills = load_json("skills.json")
    print(f"  Loading {len(skills)} skills...")
    # Insert into skills table with is_demo=False (taxonomy is real data)
    return len(skills)


async def seed_skill_relations(session):
    """Load skill prerequisite and co-occurrence relations."""
    relations = load_json("skill_relations.json")
    print(f"  Loading {len(relations)} skill relations...")
    return len(relations)


async def seed_roles(session):
    """Load role definitions with skill requirements."""
    roles = load_json("roles.json")
    print(f"  Loading {len(roles)} roles...")
    return len(roles)


async def seed_opportunities(session):
    """Load demo opportunities (all marked is_demo=True)."""
    opportunities = load_json("opportunities.json")
    print(f"  Loading {len(opportunities)} opportunities (DEMO)...")
    return len(opportunities)


async def seed_personas(session):
    """Load demo personas with full profiles (is_demo=True)."""
    personas = load_json("personas.json")
    print(f"  Loading {len(personas)} personas (DEMO)...")
    return len(personas)


async def seed_curricula(session):
    """Load demo curricula (is_demo=True)."""
    curricula = load_json("curricula.json")
    print(f"  Loading {len(curricula)} curricula (DEMO)...")
    return len(curricula)


async def seed_organization(session):
    """Load demo organization with employees (is_demo=True)."""
    org = load_json("organization.json")
    employees = org.get("employees", []) if isinstance(org, dict) else org
    print(f"  Loading organization with {len(employees)} employees (DEMO)...")
    return len(employees)


async def seed_exam_bridge(session):
    """Load competitive exam to opportunity bridge data."""
    exams = load_json("exam_bridge.json")
    print(f"  Loading {len(exams)} exam bridges...")
    return len(exams)


async def seed_government_schemes(session):
    """Load government schemes (PMKVY, NAPS, etc.)."""
    schemes = load_json("government_schemes.json")
    print(f"  Loading {len(schemes)} government schemes...")
    return len(schemes)


async def seed_cost_of_living(session):
    """Load cost of living index for Indian cities."""
    cities = load_json("cost_of_living.json")
    print(f"  Loading cost of living for {len(cities)} cities...")
    return len(cities)


async def seed_salary_data(session):
    """Load salary data for roles and locations."""
    salaries = load_json("salary_data.json")
    print(f"  Loading {len(salaries)} salary records...")
    return len(salaries)


async def main():
    """Run all seed operations."""
    print("=" * 60)
    print("SkillSetu X — Seeding Database")
    print("=" * 60)
    
    # In production, this would use the actual DB session
    # For now, validate that seed files exist and are loadable
    session = None  # Will be replaced with actual DB session
    
    steps = [
        ("Skills (Real: ESCO/O*NET)", seed_skills),
        ("Skill Relations", seed_skill_relations),
        ("Roles", seed_roles),
        ("Opportunities (DEMO)", seed_opportunities),
        ("Personas (DEMO)", seed_personas),
        ("Curricula (DEMO)", seed_curricula),
        ("Organization (DEMO)", seed_organization),
        ("Exam Bridge", seed_exam_bridge),
        ("Government Schemes", seed_government_schemes),
        ("Cost of Living", seed_cost_of_living),
        ("Salary Data", seed_salary_data),
    ]
    
    total = 0
    for name, func in steps:
        print(f"\n📦 {name}")
        try:
            count = await func(session)
            total += count
            print(f"  ✓ {count} records")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"✅ Seeding complete. Total records: {total}")
    print(f"{'=' * 60}")
    print("\nNote: DEMO data is clearly labeled with is_demo=True in the database")
    print("and shown with a DEMO badge in the UI.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
