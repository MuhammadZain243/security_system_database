$ErrorActionPreference = "Stop"

Write-Host "Loading .env..."

if (-not (Test-Path ".env")) {
    throw ".env file not found. Create it first from .env.example."
}

Get-Content ".env" | ForEach-Object {
    if ($_ -match "^\s*#" -or $_ -match "^\s*$") {
        return
    }

    $parts = $_ -split "=", 2

    if ($parts.Length -eq 2) {
        $name = $parts[0].Trim()
        $value = $parts[1].Trim().Trim('"').Trim("'")
        Set-Item -Path "Env:$name" -Value $value
    }
}

if (-not $env:DATABASE_NAME) {
    throw "DATABASE_NAME is missing in .env"
}

if (-not $env:DATABASE_USER) {
    throw "DATABASE_USER is missing in .env"
}

Write-Host "Starting PostgreSQL container..."
docker compose up -d postgres

Write-Host "Waiting for PostgreSQL to become ready..."

$maxAttempts = 30
$attempt = 0

do {
    $attempt++

    docker compose exec postgres pg_isready -U $env:DATABASE_USER -d postgres | Out-Null

    if ($LASTEXITCODE -eq 0) {
        break
    }

    Start-Sleep -Seconds 2
} while ($attempt -lt $maxAttempts)

if ($attempt -ge $maxAttempts) {
    throw "PostgreSQL did not become ready in time."
}

Write-Host "Checking database '$env:DATABASE_NAME'..."

$createDatabaseSql = @"
SELECT 'CREATE DATABASE $env:DATABASE_NAME'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = '$env:DATABASE_NAME'
)\gexec
"@

$createDatabaseSql | docker compose exec -T postgres psql -U $env:DATABASE_USER -d postgres

Write-Host "Verifying database connection..."

docker compose exec postgres psql -U $env:DATABASE_USER -d $env:DATABASE_NAME -c "SELECT current_database(), current_user;"

Write-Host "Local database is ready."
