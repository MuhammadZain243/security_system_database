# Project Commands

Useful commands for local development, Docker, database migrations, and model changes.

---

## 1. When You Change Database Models

Use this flow when you:

- Add a new model
- Add a new column
- Remove a column
- Change a column type
- Add an index
- Add a constraint
- Add a relationship

### Step 1: Format code

```powershell
uv run ruff format .
```

### Step 2: Check code style

```powershell
uv run ruff check .
```

If Ruff shows fixable errors:

```powershell
uv run ruff check . --fix
```

### Step 3: Run type checking

```powershell
uv run mypy src
```

### Step 4: Generate migration

```powershell
uv run alembic revision --autogenerate -m "describe your change"
```

Example:

```powershell
uv run alembic revision --autogenerate -m "add tenant table"
```

### Step 5: Review generated migration

Open the new file inside:

```text
migrations/versions/
```

Check that Alembic generated the correct table, column, index, or constraint changes.

### Step 6: Apply migration

```powershell
uv run alembic upgrade head
```

### Step 7: Check current migration

```powershell
uv run alembic current
```

### Step 8: Run tests

```powershell
uv run pytest
```

---

## 2. Full Check Before Commit

Run this before committing:

```powershell
uv run ruff format .
uv run ruff check .
uv run mypy src
uv run pytest
uv run alembic current
```

---

## 3. Alembic Commands

### Create migration from model changes

```powershell
uv run alembic revision --autogenerate -m "migration message"
```

### Create empty migration

Use this for manual SQL, RLS policies, extensions, triggers, or seed data.

```powershell
uv run alembic revision -m "migration message"
```

### Apply all pending migrations

```powershell
uv run alembic upgrade head
```

### Roll back one migration

```powershell
uv run alembic downgrade -1
```

### Show current migration

```powershell
uv run alembic current
```

### Show migration history

```powershell
uv run alembic history
```

### Check if model changes need migration

```powershell
uv run alembic check
```

---

## 4. Docker Commands

### Start PostgreSQL

```powershell
docker compose up -d postgres
```

### Check container status

```powershell
docker compose ps
```

### View logs

```powershell
docker compose logs postgres
```

### Follow logs

```powershell
docker compose logs -f postgres
```

Press `Ctrl+C` to stop watching logs.

### Stop PostgreSQL

```powershell
docker compose stop postgres
```

### Start stopped PostgreSQL

```powershell
docker compose start postgres
```

### Restart PostgreSQL

```powershell
docker compose restart postgres
```

### Stop and remove containers

```powershell
docker compose down
```

### Stop and delete database data

Warning: this deletes local database data.

```powershell
docker compose down -v
```

---

## 5. Database Commands

### Setup local database

```powershell
.\scripts\setup-local-db.ps1
```

### Connect to PostgreSQL

```powershell
docker compose exec postgres psql -U postgres -d security_system
```

### Run one SQL query

```powershell
docker compose exec postgres psql -U postgres -d security_system -c "SELECT current_database(), current_user;"
```

### List tables

```powershell
docker compose exec postgres psql -U postgres -d security_system -c "\dt"
```

### List schemas

```powershell
docker compose exec postgres psql -U postgres -d security_system -c "\dn"
```

### Exit psql

```sql
\q
```

---

## 6. Dependency Commands

### Install dependencies

```powershell
uv sync
```

### Add runtime dependency

```powershell
uv add package-name
```

Example:

```powershell
uv add sqlalchemy
```

### Add development dependency

```powershell
uv add --dev package-name
```

Example:

```powershell
uv add --dev pytest
```

### Export requirements.txt

```powershell
uv export --format requirements-txt --output-file requirements.txt
```

---

## 7. Testing Commands

### Run tests

```powershell
uv run pytest
```

### Run tests with detail

```powershell
uv run pytest -v
```

### Run one test file

```powershell
uv run pytest tests/test_package.py
```

---

## 8. Seed Verification Commands

### Seed Platform Super Admin

```powershell
.\scripts\seed-platform-super-admin.ps1
```

### Check platform Super Admin users

```powershell
docker compose exec postgres psql -U postgres -d security_system -c "SELECT email, status, is_super_admin FROM platform_users;"
```

### Check platform permissions

```powershell
docker compose exec postgres psql -U postgres -d security_system -c "SELECT key, name, category FROM platform_permissions ORDER BY key;"
```

### Check platform roles

```powershell
docker compose exec postgres psql -U postgres -d security_system -c "SELECT name, slug, is_system FROM platform_roles ORDER BY slug;"
```

### Count platform role permissions

```powershell
docker compose exec postgres psql -U postgres -d security_system -c "SELECT COUNT(*) FROM platform_role_permissions;"
```

---

## 9. Git Commands

### Check changed files

```powershell
git status
```

### Add files

```powershell
git add .
```

### Commit

```powershell
git commit -m "message"
```

Example:

```powershell
git commit -m "chore: initialize database package"
```

---

## 10. Recommended Daily Flow

### Start work

```powershell
docker compose up -d postgres
.\scripts\setup-local-db.ps1
uv run alembic current
```

### After changing models

```powershell
uv run ruff format .
uv run ruff check .
uv run mypy src
uv run alembic revision --autogenerate -m "describe your change"
uv run alembic upgrade head
uv run pytest
```

### Before commit

```powershell
uv run ruff format .
uv run ruff check .
uv run mypy src
uv run pytest
uv run alembic current
git status
```

---

## 11. Short Version

After changing database models, usually run:

```powershell
uv run alembic revision --autogenerate -m "describe your change"
uv run alembic upgrade head
uv run pytest
```
