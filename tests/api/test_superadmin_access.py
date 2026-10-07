from types import SimpleNamespace

from app.runtime.security import is_superadmin


def test_only_database_superadmin_role_grants_access():
    assert is_superadmin(SimpleNamespace(role="superadmin"))
    assert not is_superadmin(SimpleNamespace(role="professional"))
    assert not is_superadmin(SimpleNamespace(role="org_admin"))
    assert not is_superadmin(None)


def test_observability_endpoint_rejects_regular_account(test_client, register):
    headers, data = register()
    assert data["user"]["role"] == "professional"
    response = test_client.get("/api/v1/admin/observability", headers=headers)
    assert response.status_code == 403
