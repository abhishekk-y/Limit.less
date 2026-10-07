# Application source map

- `web`: Next.js interface, routes, journey screens, navigation, provider forms and browser checks.
- `api`: FastAPI backend and runtime migrations. `app/runtime` is the active implementation mounted by `app/main.py`.

Feature ownership and execution paths are documented in the root README. Older API routers remain as reference; moving mounted runtime modules would break imports and migrations, so they retain their established locations.
