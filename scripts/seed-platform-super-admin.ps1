$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    throw ".env file not found. Create it first from .env.example."
}

Write-Host "Seeding Platform Super Admin..."

uv run python -m security_system_database.seeds.platform_super_admin
