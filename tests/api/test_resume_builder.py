API = "/api/v1"


def test_resume_builder_saves_and_loads_private_profile(test_client, register):
    headers, _ = register("resume@example.com")
    initial = test_client.get(API + "/resume-builder", headers=headers)
    assert initial.status_code == 200
    assert initial.json()["saved"] is False
    assert initial.json()["full_name"] == "Test Learner"

    payload = {
        "full_name": "Test Learner",
        "headline": "Product designer",
        "email": "resume@example.com",
        "summary": "I design clear workflows and test them with users.",
        "skills": ["Figma", "User research", "Figma", "  "],
        "experience": [{
            "role": "Designer",
            "company": "Studio",
            "bullets": ["Mapped the onboarding journey", "  "],
        }],
        "education": [],
        "languages": ["English"],
    }
    saved = test_client.put(API + "/resume-builder", headers=headers, json=payload)
    assert saved.status_code == 200
    assert saved.json()["saved"] is True
    assert saved.json()["skills"] == ["Figma", "User research"]
    assert saved.json()["experience"][0]["bullets"] == ["Mapped the onboarding journey"]
    assert test_client.get(API + "/resume-builder", headers=headers).json()["headline"] == "Product designer"

    stranger, _ = register("other@example.com")
    assert test_client.get(API + "/resume-builder", headers=stranger).json()["saved"] is False


def test_resume_builder_bounds_content(test_client, register):
    headers, _ = register()
    response = test_client.put(API + "/resume-builder", headers=headers, json={"summary": "x" * 3001})
    assert response.status_code == 422
