# Production Files Archive

These files are not needed for the MVP but kept for future production deployment.

## Files Archived

- `docker-compose.yml` - Main Docker Compose configuration
- `docker-compose.prod.yml` - Production overrides
- `docker-compose.staging.yml` - Staging overrides
- `docker-compose.override.yml.example` - Local override example

## When You'll Need These

These files will be useful when you're ready to:
- Deploy to production with Docker
- Set up PostgreSQL and Redis
- Scale to multiple instances
- Add monitoring and logging

## Migration Path

See `MVP_CHANGES_SUMMARY.md` in the root directory for the complete migration path from MVP to production.

For now, use the simplified MVP setup documented in `STARTUP_GUIDE_MVP.md`.
