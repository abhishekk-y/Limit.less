FROM python:3.12-slim
WORKDIR /app
COPY apps/api/requirements-runtime.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/api /app/apps/api
COPY packages /app/packages
COPY integrations /app/integrations
COPY scripts /app/scripts
COPY data/seed /app/data/seed
ENV PYTHONPATH=/app:/app/apps/api
RUN useradd --create-home appuser && mkdir -p /app/.local && chown appuser:appuser /app/.local
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
