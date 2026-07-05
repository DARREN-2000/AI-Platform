# Troubleshooting

- **Database Connection Errors**: Ensure your PostgreSQL credentials in `.env` are correct.
- **Port Conflicts**: If running services locally, ensure ports 8000 (FastAPI), 3000 (React), etc., are not already in use. `kill $(lsof -t -i :<port>)` can help.
