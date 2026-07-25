# Security System Database

Canonical PostgreSQL schema, database connection configuration, session management, and migration tooling for the **Security System** platform.

`security_system_database` is an independent, versioned Python package that acts as the single source of truth for the database layer of the Security System SaaS application.

The package is consumed by:

- `security_system_backend`
- Background workers
- Scheduled jobs
- Administrative tools
- Data migration utilities
- Other Python services that need database access

The backend application does not define its own SQLAlchemy models or migrations. Database models, migrations, PostgreSQL Row-Level Security policies, seed data, and persistence-related utilities are maintained in this repository.

---

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Architecture](#2-architecture)
- [3. Technology Stack](#3-technology-stack)
- [4. Multi-Tenant Database Design](#4-multi-tenant-database-design)
- [5. Tenant Isolation](#5-tenant-isolation)
- [6. Repository Responsibilities](#6-repository-responsibilities)
- [7. Folder Structure](#7-folder-structure)
- [8. Folder and File Description](#8-folder-and-file-description)
- [9. Prerequisites](#9-prerequisites)
- [10. Install uv](#10-install-uv)
- [11. Clone the Repository](#11-clone-the-repository)
- [12. Environment Configuration](#12-environment-configuration)
- [13. Install Dependencies](#13-install-dependencies)
- [14. Add a Runtime Dependency](#14-add-a-runtime-dependency)
- [15. Add a Development Dependency](#15-add-a-development-dependency)
- [16. Start the Local PostgreSQL Database](#16-start-the-local-postgresql-database)
- [17. Stop the Local PostgreSQL Database](#17-stop-the-local-postgresql-database)
- [18. Delete the Local Database](#18-delete-the-local-database)
- [19. Connect to PostgreSQL](#19-connect-to-postgresql)
- [20. Verify the Python Package](#20-verify-the-python-package)
- [21. Verify the Database Connection](#21-verify-the-database-connection)
- [22. Alembic Migration Commands](#22-alembic-migration-commands)
- [23. Create a New Migration](#23-create-a-new-migration)
- [24. Create an Empty Migration](#24-create-an-empty-migration)
- [25. Check for Missing Migrations](#25-check-for-missing-migrations)
- [26. Run Tests](#26-run-tests)
- [27. Run Ruff](#27-run-ruff)
- [28. Run Mypy](#28-run-mypy)
- [29. Run All Quality Checks](#29-run-all-quality-checks)
- [30. Build the Python Package](#30-build-the-python-package)
- [31. Use the Package in Another Repository](#31-use-the-package-in-another-repository)
- [32. Package Usage Example](#32-package-usage-example)
- [33. Platform Session Usage](#33-platform-session-usage)
- [34. Git Commands](#34-git-commands)
- [35. Versioning](#35-versioning)
- [36. Recommended Migration Workflow](#36-recommended-migration-workflow)
- [37. Deployment Order](#37-deployment-order)
- [38. Troubleshooting](#38-troubleshooting)
- [39. Security Rules](#39-security-rules)
- [40. Current Development Status](#40-current-development-status)
- [41. Common Development Commands](#41-common-development-commands)
- [42. Quick Start](#42-quick-start)
- [43. License](#43-license)

---

## 1. Project Overview

Security System is a configurable, multi-tenant B2B SaaS platform for private security companies.

The platform is designed to provide security companies with one centralized system for managing areas such as:

- Company management
- User management
- Employee and guard management
- Client management
- Property and site management
- Shift scheduling
- Attendance management
- Leave management
- Payroll and payments
- Billing and subscriptions
- Incident reporting
- Dispatch and operations
- Notifications
- Documents
- Configurable workflows
- Configurable statuses
- Role-Based Access Control
- Audit logs
- Reports and analytics

The system is designed to avoid hard-coded tenant-specific behavior.

Each security company can eventually configure its own:

- Roles
- Permissions
- Statuses
- Workflows
- Shift rules
- Approval processes
- Notification rules
- Report settings
- Business preferences

---

## 2. Architecture

The Security System application follows a three-tier architecture.

```text
┌──────────────────────────────┐
│        Frontend Layer        │
│ React, Next.js, Web Clients  │
└───────────────┬──────────────┘
                │ HTTP / API
                ▼
┌──────────────────────────────┐
│         Backend Layer        │
│ FastAPI, Services, Use Cases │
└───────────────┬──────────────┘
                │ SQLAlchemy
                ▼
┌──────────────────────────────┐
│        Database Layer        │
│ PostgreSQL, Alembic, RLS     │
└──────────────────────────────┘
```

This repository represents the **Database Layer**.

It contains database-only responsibilities and does not contain HTTP routes, API controllers, frontend logic, or complete business workflows.

---

## 3. Technology Stack

| Area                       | Technology        |
| -------------------------- | ----------------- |
| Database                   | PostgreSQL        |
| Programming language       | Python 3.12+      |
| ORM and schema toolkit     | SQLAlchemy 2.x    |
| PostgreSQL driver          | Psycopg 3         |
| Migration tool             | Alembic           |
| Configuration              | Pydantic Settings |
| Package manager            | uv                |
| Testing                    | Pytest            |
| Type checking              | Mypy              |
| Linting and formatting     | Ruff              |
| Local database environment | Docker Compose    |

---

## 4. Multi-Tenant Database Design

The platform uses the following tenancy model:

```text
Shared PostgreSQL Database
        +
Shared Database Schema
        +
tenant_id on tenant-owned tables
        +
PostgreSQL Row-Level Security
```

Every tenant-owned table will include a `tenant_id` column.

Examples of tenant-owned records include:

- Employees
- Guards
- Clients
- Properties
- Sites
- Shifts
- Attendance records
- Leave requests
- Incidents
- Documents
- Payroll records

Platform-owned tables may not require a `tenant_id`.

Examples may include:

- Platform tenants
- Platform administrators
- Subscription plans
- Global system configuration
- Migration metadata

---

## 5. Tenant Isolation

Application code must never trust a tenant ID supplied directly in a request body.

The active tenant should be resolved from a trusted source such as:

- Authenticated user session
- Access token
- API key
- Verified subdomain
- Trusted internal service identity

After resolving the tenant, the application opens a tenant-scoped transaction.

```python
from security_system_database import tenant_session

with tenant_session(SessionFactory, tenant_id) as session:
    ...
```

The transaction sets the PostgreSQL session variable:

```sql
SET LOCAL app.current_tenant_id = '<tenant-id>';
```

PostgreSQL Row-Level Security policies can use this value to restrict records to the active tenant.

Application-level filtering remains necessary. Row-Level Security acts as an additional defense layer.

---

## 6. Repository Responsibilities

This repository owns:

- SQLAlchemy declarative base
- SQLAlchemy models
- Database constraints
- Database indexes
- Database enums
- Database connection settings
- SQLAlchemy engine creation
- Session factory creation
- Tenant-scoped transactions
- Platform-scoped transactions
- Alembic migrations
- PostgreSQL Row-Level Security policies
- Initial seed data
- Persistence-only repositories
- Database tests
- Database package releases

This repository does not own:

- FastAPI routes
- HTTP controllers
- Request validation models
- API response models
- Authentication endpoints
- Frontend components
- User interface behavior
- Complete business workflows
- Email templates
- Notification delivery
- Background job orchestration

These responsibilities belong to the backend or frontend repositories.

---

## 7. Folder Structure

```text
security_system_database/
├── src/
│   └── security_system_database/
│       ├── __init__.py
│       ├── base.py
│       ├── config.py
│       ├── session.py
│       └── py.typed
│
├── migrations/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
│
├── tests/
│   └── test_package.py
│
├── .env
├── .env.example
├── .gitignore
├── .python-version
├── alembic.ini
├── compose.yaml
├── pyproject.toml
├── README.md
└── uv.lock
```

Future folders will be added as database development progresses.

```text
src/security_system_database/
├── models/
├── repositories/
├── rls/
├── seeds/
├── types/
├── constants/
└── utilities/
```

---

## 8. Folder and File Description

### `src/security_system_database/`

Contains the installable Python package.

Anything placed inside this directory can be imported by other Python applications after installing the package.

---

### `src/security_system_database/__init__.py`

Defines the public API of the package.

Consuming applications should preferably import commonly used objects from the package root.

```python
from security_system_database import (
    Base,
    DatabaseSettings,
    build_engine,
    build_session_factory,
    tenant_session,
)
```

---

### `src/security_system_database/config.py`

Contains the database configuration model.

It reads environment variables beginning with `DATABASE_`.

Examples:

```dotenv
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=security_system
DATABASE_USER=security_system
DATABASE_PASSWORD=security_system_local_password
```

Database configuration should not be read through scattered `os.environ.get()` calls.

All database-related configuration should be added to `DatabaseSettings`.

---

### `src/security_system_database/base.py`

Contains the shared SQLAlchemy declarative `Base`.

Every SQLAlchemy model must inherit from this same base.

```python
from security_system_database import Base
```

Using one shared metadata object allows Alembic to detect the complete database schema.

This file also defines the database constraint naming convention.

---

### `src/security_system_database/session.py`

Contains:

- SQLAlchemy engine creation
- Session factory creation
- Tenant-scoped transaction helper
- Platform-scoped transaction helper

The engine and session factory should be created once when an application starts.

A new database session should be created for each request or use case.

---

### `src/security_system_database/py.typed`

Marks the package as a typed Python package according to PEP 561.

This allows consuming applications to use type information from the package.

---

### `migrations/`

Contains the Alembic migration environment.

Database schema changes are version-controlled through migration files.

---

### `migrations/env.py`

Connects Alembic with:

- `DatabaseSettings`
- SQLAlchemy engine
- `Base.metadata`
- PostgreSQL database

When new model modules are created, they must be imported before Alembic reads `Base.metadata`.

---

### `migrations/versions/`

Contains generated migration revisions.

Example:

```text
migrations/versions/
└── a1b2c3d4e5f6_create_tenants_table.py
```

Migration files must be committed to Git.

Autogenerated migration files must always be manually reviewed.

---

### `migrations/script.py.mako`

Template used by Alembic when generating new migration files.

---

### `alembic.ini`

Contains Alembic CLI and logging configuration.

Database credentials must not be stored in this file.

The actual connection details are loaded through `DatabaseSettings`.

---

### `tests/`

Contains automated tests for the package.

Future test categories may include:

```text
tests/
├── unit/
├── integration/
├── migrations/
├── repositories/
└── rls/
```

---

### `.env.example`

Documents the environment variables required to run the project.

This file is committed to Git.

It must not contain real production credentials.

---

### `.env`

Contains local environment values.

This file must not be committed to Git.

---

### `compose.yaml`

Defines the local PostgreSQL Docker container.

It is used for local development and testing.

---

### `pyproject.toml`

Contains:

- Package metadata
- Python version requirement
- Runtime dependencies
- Development dependencies
- Ruff configuration
- Mypy configuration
- Pytest configuration
- Build-system configuration

---

### `uv.lock`

Contains exact resolved dependency versions.

This file should be committed to Git.

Do not manually edit it.

---

### `.python-version`

Defines the Python version used by uv for this project.

---

## 9. Prerequisites

Install the following tools before running the project:

- Git
- Docker Desktop
- uv
- Python 3.12 or uv-managed Python 3.12
- VS Code or another code editor

Verify the tools:

```powershell
git --version
docker --version
docker compose version
uv --version
```

---

## 10. Install uv

On Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart PowerShell and verify:

```powershell
uv --version
```

Install Python 3.12 through uv:

```powershell
uv python install 3.12
```

List available Python installations:

```powershell
uv python list
```

---

## 11. Clone the Repository

```powershell
git clone https://github.com/<organization>/security_system_database.git
```

Enter the project directory:

```powershell
cd security_system_database
```

When creating the project locally before pushing it to GitHub:

```powershell
uv init --lib --python 3.12 security_system_database
cd security_system_database
git init
```

---

## 12. Environment Configuration

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

On Linux or macOS:

```bash
cp .env.example .env
```

Open `.env` and configure the local database values.

```dotenv
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=security_system
DATABASE_USER=security_system
DATABASE_PASSWORD=security_system_local_password

DATABASE_SSL_MODE=disable
DATABASE_ECHO=false

DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT_SECONDS=30
DATABASE_POOL_RECYCLE_SECONDS=1800
DATABASE_CONNECT_TIMEOUT_SECONDS=10
```

For local Docker development:

```dotenv
DATABASE_SSL_MODE=disable
```

Production environments should normally use a secure SSL mode such as:

```dotenv
DATABASE_SSL_MODE=require
```

or:

```dotenv
DATABASE_SSL_MODE=verify-full
```

---

## 13. Install Dependencies

Install all runtime and development dependencies:

```powershell
uv sync
```

This command:

- Creates the local `.venv`
- Installs dependencies from `pyproject.toml`
- Uses exact versions from `uv.lock`
- Installs the local package in the environment

Do not manually create the virtual environment when using uv.

---

## 14. Add a Runtime Dependency

Example:

```powershell
uv add sqlalchemy
```

Add Alembic:

```powershell
uv add alembic
```

Add Psycopg:

```powershell
uv add psycopg
```

Add Pydantic Settings:

```powershell
uv add pydantic-settings
```

Add a constrained version:

```powershell
uv add "sqlalchemy>=2.0,<3"
```

---

## 15. Add a Development Dependency

Example:

```powershell
uv add --dev pytest
```

Add Ruff:

```powershell
uv add --dev ruff
```

Add Mypy:

```powershell
uv add --dev mypy
```

Add Psycopg binary implementation for local development:

```powershell
uv add --dev "psycopg[binary]"
```

Synchronize dependencies after modifying `pyproject.toml`:

```powershell
uv sync
```

---

## 16. Start the Local PostgreSQL Database

Start PostgreSQL:

```powershell
docker compose up -d postgres
```

Check container status:

```powershell
docker compose ps
```

View database logs:

```powershell
docker compose logs postgres
```

Follow logs continuously:

```powershell
docker compose logs -f postgres
```

Press `Ctrl+C` to exit the log viewer.

This does not stop the PostgreSQL container.

---

## 17. Stop the Local PostgreSQL Database

Stop PostgreSQL without removing the container:

```powershell
docker compose stop postgres
```

Start the stopped container again:

```powershell
docker compose start postgres
```

Stop and remove the containers:

```powershell
docker compose down
```

The database data remains because it is stored in a Docker volume.

---

## 18. Delete the Local Database

Warning: the following command permanently deletes the local PostgreSQL volume and all local database data.

```powershell
docker compose down -v
```

Start a new empty database:

```powershell
docker compose up -d postgres
```

Run migrations again:

```powershell
uv run alembic upgrade head
```

---

## 19. Connect to PostgreSQL

Open a PostgreSQL shell inside the container:

```powershell
docker compose exec postgres psql -U security_system -d security_system
```

Exit the PostgreSQL shell:

```sql
\q
```

Run a single query:

```powershell
docker compose exec postgres psql -U security_system -d security_system -c "SELECT current_database(), current_user;"
```

List tables:

```powershell
docker compose exec postgres psql -U security_system -d security_system -c "\dt"
```

List schemas:

```powershell
docker compose exec postgres psql -U security_system -d security_system -c "\dn"
```

List database roles:

```powershell
docker compose exec postgres psql -U security_system -d security_system -c "\du"
```

---

## 20. Verify the Python Package

Test the package import:

```powershell
uv run python -c "import security_system_database; print('Package imported successfully')"
```

Expected output:

```text
Package imported successfully
```

---

## 21. Verify the Database Connection

Run:

```powershell
uv run python -c "from sqlalchemy import text; from security_system_database import build_engine; engine = build_engine(); connection = engine.connect(); print(connection.execute(text('SELECT current_database(), current_user')).one()); connection.close(); engine.dispose()"
```

Expected output:

```text
('security_system', 'security_system')
```

A shorter connection check:

```powershell
uv run python -c "from security_system_database import build_engine; connection = build_engine().connect(); print('connected'); connection.close()"
```

---

## 22. Alembic Migration Commands

### Check the current revision

```powershell
uv run alembic current
```

### View migration history

```powershell
uv run alembic history
```

### View detailed migration history

```powershell
uv run alembic history --verbose
```

### Apply all pending migrations

```powershell
uv run alembic upgrade head
```

### Apply the next migration

```powershell
uv run alembic upgrade +1
```

### Roll back one migration

```powershell
uv run alembic downgrade -1
```

### Roll back to the base revision

```powershell
uv run alembic downgrade base
```

### Upgrade to a specific revision

```powershell
uv run alembic upgrade <revision-id>
```

### Downgrade to a specific revision

```powershell
uv run alembic downgrade <revision-id>
```

---

## 23. Create a New Migration

After creating or updating SQLAlchemy models:

```powershell
uv run alembic revision --autogenerate -m "add employee table"
```

Another example:

```powershell
uv run alembic revision --autogenerate -m "add tenant configuration tables"
```

Review the generated file inside:

```text
migrations/versions/
```

Apply it:

```powershell
uv run alembic upgrade head
```

Never apply an autogenerated migration without reviewing:

- Created tables
- Removed tables
- Added columns
- Removed columns
- Foreign keys
- Unique constraints
- Check constraints
- Indexes
- Column defaults
- Data type changes
- Upgrade logic
- Downgrade logic

---

## 24. Create an Empty Migration

Use an empty migration when adding manual SQL, PostgreSQL extensions, RLS policies, triggers, functions, or data migrations.

```powershell
uv run alembic revision -m "enable row level security"
```

Open the generated migration and add the required operations manually.

Example:

```python
from alembic import op


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE employees ENABLE ROW LEVEL SECURITY
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE employees DISABLE ROW LEVEL SECURITY
        """
    )
```

Apply the migration:

```powershell
uv run alembic upgrade head
```

---

## 25. Check for Missing Migrations

After changing SQLAlchemy models:

```powershell
uv run alembic check
```

This command checks whether Alembic detects model changes that have not yet been converted into a migration.

---

## 26. Run Tests

Run all tests:

```powershell
uv run pytest
```

Run tests with detailed output:

```powershell
uv run pytest -v
```

Run a specific test file:

```powershell
uv run pytest tests/test_package.py
```

Run a specific test:

```powershell
uv run pytest tests/test_package.py::test_database_settings_build_psycopg_url
```

Stop after the first failure:

```powershell
uv run pytest -x
```

Show print output:

```powershell
uv run pytest -s
```

Run coverage:

```powershell
uv run pytest --cov=security_system_database
```

Generate an HTML coverage report:

```powershell
uv run pytest --cov=security_system_database --cov-report=html
```

Open:

```text
htmlcov/index.html
```

---

## 27. Run Ruff

Check linting:

```powershell
uv run ruff check .
```

Automatically fix safe linting issues:

```powershell
uv run ruff check . --fix
```

Check formatting without changing files:

```powershell
uv run ruff format . --check
```

Format all supported files:

```powershell
uv run ruff format .
```

---

## 28. Run Mypy

Run type checking:

```powershell
uv run mypy src
```

Check both the source code and tests:

```powershell
uv run mypy src tests
```

---

## 29. Run All Quality Checks

Windows PowerShell:

```powershell
uv run ruff format .
uv run ruff check .
uv run mypy src
uv run pytest
```

Run them as one PowerShell command:

```powershell
uv run ruff format .; uv run ruff check .; uv run mypy src; uv run pytest
```

Linux or macOS:

```bash
uv run ruff format . && \
uv run ruff check . && \
uv run mypy src && \
uv run pytest
```

---

## 30. Build the Python Package

Build the distributable package:

```powershell
uv build
```

This creates:

```text
dist/
├── security_system_database-<version>.tar.gz
└── security_system_database-<version>-py3-none-any.whl
```

Check the generated files:

```powershell
Get-ChildItem dist
```

---

## 31. Use the Package in Another Repository

For local development, install the database package using its local path.

From the backend repository:

```powershell
uv add "../security_system_database"
```

For an editable local dependency:

```powershell
uv add --editable "../security_system_database"
```

Install it from Git:

```powershell
uv add "security-system-database @ git+https://github.com/<organization>/security_system_database.git@main"
```

Install a tagged version:

```powershell
uv add "security-system-database @ git+https://github.com/<organization>/security_system_database.git@v0.1.0"
```

After publishing it to a private Python package index:

```powershell
uv add "security-system-database==0.1.0"
```

---

## 32. Package Usage Example

```python
from uuid import UUID

from security_system_database import (
    DatabaseSettings,
    build_engine,
    build_session_factory,
    tenant_session,
)


settings = DatabaseSettings()

engine = build_engine(settings)

SessionFactory = build_session_factory(engine)

tenant_id = UUID("00000000-0000-0000-0000-000000000001")

with tenant_session(SessionFactory, tenant_id) as session:
    # Execute tenant-scoped database operations here.
    pass
```

The engine and session factory should be created once during application startup.

Do not create a new engine for every API request.

---

## 33. Platform Session Usage

Platform sessions are intended for approved control-plane operations that do not have a tenant context.

```python
from security_system_database import (
    build_engine,
    build_session_factory,
    platform_session,
)


engine = build_engine()
SessionFactory = build_session_factory(engine)

with platform_session(SessionFactory) as session:
    ...
```

A platform session does not automatically bypass PostgreSQL Row-Level Security.

Separate database roles or explicit administrative policies may be required for privileged operations.

---

## 34. Git Commands

Check repository status:

```powershell
git status
```

Add all changed files:

```powershell
git add .
```

Commit changes:

```powershell
git commit -m "chore: initialize database package"
```

Push the current branch:

```powershell
git push
```

Create a new branch:

```powershell
git checkout -b feature/add-tenant-model
```

Modern Git syntax:

```powershell
git switch -c feature/add-tenant-model
```

Check whether `.env` is ignored:

```powershell
git check-ignore .env
```

Expected output:

```text
.env
```

---

## 35. Versioning

The package follows semantic versioning.

```text
MAJOR.MINOR.PATCH
```

Example:

```text
0.1.0
```

Version meanings:

- `PATCH`: backward-compatible fixes
- `MINOR`: backward-compatible functionality
- `MAJOR`: incompatible changes

Examples:

```text
0.1.0   Initial database package
0.2.0   Add tenant and organization models
0.3.0   Add configurable RBAC models
1.0.0   First production-stable schema package
```

Create a Git tag:

```powershell
git tag v0.1.0
```

Push the tag:

```powershell
git push origin v0.1.0
```

Push all tags:

```powershell
git push origin --tags
```

---

## 36. Recommended Migration Workflow

For every schema change:

1. Update or add SQLAlchemy models.
2. Run formatting and linting.
3. Generate a migration.
4. Review the migration manually.
5. Apply the migration locally.
6. Run tests.
7. Test the downgrade when possible.
8. Reapply the migration.
9. Commit the models and migration together.
10. Deploy the migration before deploying a backend version that depends on it.

Commands:

```powershell
uv run ruff format .
uv run ruff check .
uv run mypy src
uv run alembic revision --autogenerate -m "describe the schema change"
uv run alembic upgrade head
uv run pytest
uv run alembic downgrade -1
uv run alembic upgrade head
```

---

## 37. Deployment Order

Database migrations are deployed independently of the backend.

The recommended deployment order is:

```text
1. Back up the target database
2. Deploy backward-compatible database migrations
3. Verify the migration
4. Deploy the backend version that uses the new schema
5. Deploy workers and supporting services
6. Deploy the frontend when required
7. Remove deprecated columns in a later release
```

The backend must not automatically run:

```text
alembic upgrade head
```

during application startup.

Migrations should run as a dedicated deployment step.

---

## 38. Troubleshooting

### PostgreSQL container is not running

Check:

```powershell
docker compose ps
```

View logs:

```powershell
docker compose logs postgres
```

Restart the container:

```powershell
docker compose restart postgres
```

---

### Port 5432 is already in use

Change `.env`:

```dotenv
DATABASE_PORT=5433
```

Recreate the container:

```powershell
docker compose down
docker compose up -d postgres
```

---

### Database credentials were changed but PostgreSQL still uses old values

The official PostgreSQL image uses the initialization environment variables only when the database volume is created.

Delete the local database volume:

```powershell
docker compose down -v
```

Create it again:

```powershell
docker compose up -d postgres
```

Warning: this deletes all local database data.

---

### Python package cannot be imported

Synchronize dependencies:

```powershell
uv sync
```

Test the import:

```powershell
uv run python -c "import security_system_database"
```

Verify the package exists:

```text
src/security_system_database/
```

---

### Alembic cannot find the models

Make sure:

- Every model inherits from the shared `Base`
- Model modules are imported before Alembic reads `Base.metadata`
- `target_metadata` points to `Base.metadata`
- The model file is part of the installed package

Example inside `migrations/env.py`:

```python
import security_system_database.models  # noqa: F401

target_metadata = Base.metadata
```

---

### Alembic detects no schema changes

Run:

```powershell
uv run alembic check
```

Verify that the model module is imported.

Verify that the model inherits from:

```python
from security_system_database import Base
```

Do not create a separate `DeclarativeBase` in each model file.

---

### Environment variables are not loading

Check whether `.env` exists:

```powershell
Test-Path .env
```

Expected output:

```text
True
```

Print non-sensitive settings:

```powershell
uv run python -c "from security_system_database import DatabaseSettings; settings = DatabaseSettings(); print(settings.host, settings.port, settings.name, settings.user)"
```

Do not print passwords in logs.

---

### Reset the local environment

Remove the virtual environment:

```powershell
Remove-Item -Recurse -Force .venv
```

Reinstall dependencies:

```powershell
uv sync
```

Reset PostgreSQL:

```powershell
docker compose down -v
docker compose up -d postgres
uv run alembic upgrade head
```

Warning: resetting PostgreSQL deletes all local database data.

---

## 39. Security Rules

The following rules are mandatory:

- Never commit `.env`
- Never commit production credentials
- Never store passwords in `alembic.ini`
- Never trust a tenant ID from a request body
- Never rely only on frontend tenant filtering
- Never create tenant-owned records without a tenant context
- Never use platform sessions for normal tenant requests
- Never disable Row-Level Security to solve an application bug
- Never run unreviewed autogenerated migrations
- Never modify a migration after it has been deployed to a shared environment
- Never allow the backend to silently manage production migrations
- Never log database passwords
- Never use the database owner role for normal application traffic

---

## 40. Current Development Status

The initial infrastructure includes:

- Python package structure
- uv dependency management
- PostgreSQL local container
- Environment-based configuration
- SQLAlchemy declarative base
- Constraint naming conventions
- SQLAlchemy engine builder
- SQLAlchemy session factory
- Tenant-scoped transaction helper
- Platform-scoped transaction helper
- Alembic migration environment
- Baseline migration
- Ruff configuration
- Mypy configuration
- Pytest configuration

The following features will be added in later phases:

- Shared model mixins
- UUID primary keys
- Tenant models
- User and identity models
- Configurable RBAC
- Configurable statuses
- Dynamic workflows
- Employee and guard models
- Client and property models
- Shift scheduling models
- Attendance models
- Leave models
- Incident models
- Billing models
- Audit logging
- Row-Level Security policies
- Seed data
- Repository layer
- Integration tests
- Migration tests

---

## 41. Common Development Commands

Install dependencies:

```powershell
uv sync
```

Start PostgreSQL:

```powershell
docker compose up -d postgres
```

Check PostgreSQL:

```powershell
docker compose ps
```

Apply migrations:

```powershell
uv run alembic upgrade head
```

Create a migration:

```powershell
uv run alembic revision --autogenerate -m "migration description"
```

Run formatting:

```powershell
uv run ruff format .
```

Run linting:

```powershell
uv run ruff check .
```

Run type checking:

```powershell
uv run mypy src
```

Run tests:

```powershell
uv run pytest
```

Build the package:

```powershell
uv build
```

Stop PostgreSQL:

```powershell
docker compose down
```

---

## 42. Quick Start

```powershell
git clone https://github.com/<organization>/security_system_database.git
cd security_system_database

Copy-Item .env.example .env

uv sync

docker compose up -d postgres

uv run alembic upgrade head

uv run ruff check .
uv run mypy src
uv run pytest
```

Verify the connection:

```powershell
uv run python -c "from security_system_database import build_engine; connection = build_engine().connect(); print('Database connected successfully'); connection.close()"
```

---

## 43. License

This project is private and intended for the Security System platform.

Unauthorized copying, distribution, modification, or publication is prohibited unless permission is provided by the project owner.
