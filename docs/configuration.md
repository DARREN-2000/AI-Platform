# Configuration

The platform uses `.env` files for configuration. A `.env.example` is provided in each repository.

## Global Settings

- `JWT_SECRET`: The shared secret or public key used to validate JWTs across services.
- `REDIS_URL`: Connection string for the centralized Redis cache.
- `DATABASE_URL`: Connection string for the primary PostgreSQL database.

## Service-Specific Settings

*Refer to the individual service directories for specific configuration requirements.*
