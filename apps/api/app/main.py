"""API entry point. All mounted endpoints use persistent, tenant-scoped services."""
from app.runtime.app import create_app

app = create_app()
