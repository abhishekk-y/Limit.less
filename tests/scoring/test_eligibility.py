import pytest
from datetime import date

def calculate_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def is_eligible(candidate, requirements):
    if 'min_age' in requirements and calculate_age(candidate['dob']) < requirements['min_age']:
        return False
    if 'max_age' in requirements and calculate_age(candidate['dob']) > requirements['max_age']:
        return False
    if 'education' in requirements and candidate['education'] not in requirements['education']:
        return False
    return True

def test_age_eligibility():
    candidate = {'dob': date(2000, 1, 1), 'education': 'B.Tech'}
    # Age is around 26 (depending on run year)
    # Let's mock a deterministic age for testing
    age = calculate_age(candidate['dob'])
    
    req_pass = {'min_age': age - 2, 'max_age': age + 2}
    req_fail = {'min_age': age + 2, 'max_age': age + 5}
    
    assert is_eligible(candidate, req_pass) == True
    assert is_eligible(candidate, req_fail) == False

def test_education_eligibility():
    candidate = {'dob': date(2000, 1, 1), 'education': 'B.Tech'}
    req_pass = {'education': ['B.Tech', 'M.Tech']}
    req_fail = {'education': ['MBA']}
    
    assert is_eligible(candidate, req_pass) == True
    assert is_eligible(candidate, req_fail) == False
