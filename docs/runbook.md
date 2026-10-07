# Operations Runbook

## Incident Response
1. **API Down**: Check Render dashboard and restart web service.
2. **Database Errors**: Verify Neon Serverless status. Check connection pooling in Upstash.
3. **Stale Data**: Run `python scripts/refresh_data.py` to pull the latest job market metrics.

## Routine Maintenance
- **Weekly**: Audit adversarial profiles against the sanitizer.
- **Monthly**: Retrain STS embeddings if new skill taxonomies are introduced.
