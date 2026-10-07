API = "/api/v1"


def test_assessment_grades_server_side_and_preserves_best_score(test_client, register):
    headers, _ = register()
    bank = test_client.get(API + "/assessments", headers=headers).json()
    assert all("answer" not in q for a in bank for q in a["questions"])
    result = test_client.post(
        API + "/assessments/python/submit",
        headers=headers,
        json={"answers": {"0": 1, "1": 0, "2": 2, "3": 0}},
    )
    assert result.status_code == 200
    assert result.json()["score"] == 100
    twin = test_client.get(API + "/talent-twin", headers=headers).json()
    assert twin["skills"][0]["score"] == 40
    assert twin["skills"][0]["verified"] is False
    result = test_client.post(
        API + "/assessments/python/submit",
        headers=headers,
        json={"answers": {"0": 0, "1": 1, "2": 0, "3": 1}},
    )
    assert result.json()["score"] == 0
    assert result.json()["best_score"] == 100
    assert (
        test_client.post(
            API + "/assessments/python/submit", headers=headers, json={"answers": {}}
        ).status_code
        == 422
    )


def test_sas_foundations_badge_is_scoped_and_not_claimed_as_sas_certification(test_client, register):
    headers, _ = register()
    assessments = test_client.get(API + "/assessments", headers=headers).json()
    sas = next(item for item in assessments if item["skill_id"] == "sas_foundations")
    assert len(sas["questions"]) == 8
    assert "not a SAS-issued" in sas["limitations"]
    response = test_client.post(API + "/assessments/sas_foundations/submit", headers=headers,
        json={"answers": {str(index): 0 for index in range(8)}})
    assert response.status_code == 200
    badge = response.json()["platform_credential"]
    assert badge["issuer"] == "Limit.less"
    assert badge["not_sas_issued"] is True
    assert "identity" in badge["verification"]
    updated = test_client.get(API + "/assessments", headers=headers).json()
    sas = next(item for item in updated if item["skill_id"] == "sas_foundations")
    assert sas["platform_credential"]["credential_id"] == badge["credential_id"]


def test_sas_foundations_badge_requires_pass_threshold(test_client, register):
    headers, _ = register()
    response = test_client.post(API + "/assessments/sas_foundations/submit", headers=headers,
        json={"answers": {str(index): (0 if index < 5 else 1) for index in range(8)}})
    assert response.status_code == 200
    assert response.json()["score"] == 62.5
    assert response.json()["platform_credential"] is None


def test_passport_consent_minimization_and_revocation(test_client, register):
    headers, _ = register()
    assert (
        test_client.post(API + "/passport/share", headers=headers, json={"consent": False}).status_code == 422
    )
    response = test_client.post(API + "/passport/share", headers=headers, json={"consent": True})
    assert response.status_code == 201
    share = response.json()
    token = share["path"].split("/")[-1]
    public = test_client.get(API + "/public/passport/" + token)
    assert public.status_code == 200
    assert "email" not in public.json()
    assert "document" not in public.json()
    stranger, _ = register("stranger@example.com")
    assert test_client.delete(API + "/passport/shares/" + share["id"], headers=stranger).status_code == 404
    assert test_client.delete(API + "/passport/shares/" + share["id"], headers=headers).status_code == 204
    assert test_client.get(API + "/public/passport/" + token).status_code == 404


def test_account_deletion_removes_public_passport(test_client, register):
    headers, _ = register()
    share = test_client.post(API + "/passport/share", headers=headers, json={"consent": True}).json()
    test_client.post(API + "/privacy/delete", headers=headers, json={"confirmation": "DELETE MY DATA"})
    assert test_client.get(API + "/public/passport/" + share["path"].split("/")[-1]).status_code == 404
