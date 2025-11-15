# PostgreSQL Setup Guide

This guide will help you set up PostgreSQL with Docker for local development.

## Prerequisites

- Docker installed on your system
- Docker Compose installed

## Setup Steps

### 1. Start PostgreSQL with Docker

Run the following command in the project root directory:

```bash
docker-compose up -d
```

This will:
- Pull the PostgreSQL 16 Alpine image
- Create a container named `homeless_assistant_db`
- Expose PostgreSQL on port 5432
- Create a persistent volume for data storage

### 2. Configure Environment Variables

Copy the example environment file and update it:

```bash
cd backend
cp .env.example .env
```

Edit the `.env` file and ensure the DATABASE_URL is set to PostgreSQL:

```env
DATABASE_URL=postgresql://homeless_assistant:dev_password_change_in_production@localhost:5432/homeless_assistant_db
```

### 3. Install Python Dependencies

Install the updated dependencies (including psycopg2):

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Initialize the Database

Run your FastAPI application to create the database tables:

```bash
python main.py
# or
uvicorn main:app --reload
```

The SQLAlchemy models will automatically create the necessary tables in PostgreSQL.

## Docker Commands

### View logs
```bash
docker-compose logs -f postgres
```

### Stop PostgreSQL
```bash
docker-compose stop
```

### Start PostgreSQL (after stopping)
```bash
docker-compose start
```

### Stop and remove containers
```bash
docker-compose down
```

### Stop and remove containers + volumes (deletes all data)
```bash
docker-compose down -v
```

## Database Connection Details

- **Host**: localhost
- **Port**: 5432
- **Database**: homeless_assistant_db
- **Username**: homeless_assistant
- **Password**: dev_password_change_in_production

**Note**: Change the password in production!

## Connecting with psql (Optional)

You can connect to the database using psql:

```bash
docker exec -it homeless_assistant_db psql -U homeless_assistant -d homeless_assistant_db
```

## Database Management Tools

You can also use GUI tools to manage your PostgreSQL database:

- **pgAdmin**: https://www.pgadmin.org/
- **DBeaver**: https://dbeaver.io/
- **DataGrip**: https://www.jetbrains.com/datagrip/

Connection details are the same as listed above.

## Switching Between SQLite and PostgreSQL

The application supports both SQLite and PostgreSQL. To switch:

1. **For SQLite**: Update your `.env` file:
   ```env
   DATABASE_URL=sqlite:///./homeless_assistant.db
   ```

2. **For PostgreSQL**: Update your `.env` file:
   ```env
   DATABASE_URL=postgresql://homeless_assistant:dev_password_change_in_production@localhost:5432/homeless_assistant_db
   ```

The `database.py` file automatically handles the configuration differences between the two databases.

## Troubleshooting

### Port 5432 already in use
If you have another PostgreSQL instance running, either stop it or change the port in `docker-compose.yml`:
```yaml
ports:
  - "5433:5432"  # Changed from 5432:5432
```
Then update your DATABASE_URL to use port 5433.

### Connection refused
Make sure the Docker container is running:
```bash
docker ps | grep homeless_assistant_db
```

### Database doesn't exist
The database is created automatically when the container starts. If you removed the volume, restart the container:
```bash
docker-compose down
docker-compose up -d
```

## Production Considerations

When deploying to production:

1. **Change the default password** in `docker-compose.yml` and `.env`
2. **Use environment variables** instead of hardcoded credentials
3. **Enable SSL/TLS** for database connections
4. **Set up regular backups** of your PostgreSQL data
5. **Use a managed PostgreSQL service** (AWS RDS, Google Cloud SQL, etc.) instead of self-hosting
