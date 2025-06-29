# PostgreSQL Setup Script for Housing Price Analysis System
# Simple version with minimal Chinese characters to avoid encoding issues

param(
    [string]$PostgresPassword = "",
    [switch]$SkipUserInput
)

# Set encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Database Setup for Housing Price System" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is installed
Write-Host "Checking PostgreSQL installation..." -ForegroundColor Yellow

$postgresqlInstalled = $false
$psqlPath = ""

# Common PostgreSQL installation paths
$commonPaths = @(
    "C:\Program Files\PostgreSQL\*\bin\psql.exe",
    "C:\Program Files (x86)\PostgreSQL\*\bin\psql.exe",
    "C:\PostgreSQL\*\bin\psql.exe"
)

foreach ($path in $commonPaths) {
    $found = Get-ChildItem $path -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $psqlPath = $found.FullName
        $postgresqlInstalled = $true
        break
    }
}

# Try to find in PATH
if (-not $postgresqlInstalled) {
    try {
        $result = Get-Command psql -ErrorAction SilentlyContinue
        if ($result) {
            $psqlPath = $result.Source
            $postgresqlInstalled = $true
        }
    } catch {
        # psql not in PATH
    }
}

if (-not $postgresqlInstalled) {
    Write-Host "ERROR: PostgreSQL not installed or not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install PostgreSQL:" -ForegroundColor Yellow
    Write-Host "1. Visit: https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
    Write-Host "2. Download PostgreSQL 12 or higher" -ForegroundColor Cyan
    Write-Host "3. Remember the postgres user password during installation" -ForegroundColor Cyan
    Write-Host ""
    if (-not $SkipUserInput) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

Write-Host "SUCCESS: PostgreSQL found at: $psqlPath" -ForegroundColor Green

# Get postgres password if not provided
if ([string]::IsNullOrEmpty($PostgresPassword) -and -not $SkipUserInput) {
    Write-Host ""
    $PostgresPassword = Read-Host "Enter postgres user password" -AsSecureString
    $PostgresPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($PostgresPassword))
}

if ([string]::IsNullOrEmpty($PostgresPassword)) {
    Write-Host "ERROR: No password provided" -ForegroundColor Red
    if (-not $SkipUserInput) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Set environment variable for password
$env:PGPASSWORD = $PostgresPassword

Write-Host ""
Write-Host "Testing PostgreSQL connection..." -ForegroundColor Yellow

try {
    $testConnection = & $psqlPath -h localhost -U postgres -d postgres -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Cannot connect to PostgreSQL" -ForegroundColor Red
        Write-Host "Error: $testConnection" -ForegroundColor Red
        if (-not $SkipUserInput) {
            Read-Host "Press Enter to exit"
        }
        exit 1
    }
    Write-Host "SUCCESS: Connected to PostgreSQL" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to execute psql command: $($_.Exception.Message)" -ForegroundColor Red
    if (-not $SkipUserInput) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Create application database and user
Write-Host ""
Write-Host "Creating application database and user..." -ForegroundColor Blue

# Check if user exists
Write-Host "Checking user Housing_Price_postgres..." -ForegroundColor Yellow
$checkUser = & $psqlPath -h localhost -U postgres -d postgres -t -c "SELECT 1 FROM pg_roles WHERE rolname='Housing_Price_postgres';" 2>&1

if ($checkUser -match "1") {
    Write-Host "WARNING: User Housing_Price_postgres already exists" -ForegroundColor Yellow
} else {
    Write-Host "Creating user Housing_Price_postgres..." -ForegroundColor Blue
    $createUser = & $psqlPath -h localhost -U postgres -d postgres -c "CREATE USER Housing_Price_postgres WITH PASSWORD '123456';" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: User created successfully" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to create user: $createUser" -ForegroundColor Red
    }
}

# Check if database exists
Write-Host "Checking database Housing_Price_postgres..." -ForegroundColor Yellow
$checkDB = & $psqlPath -h localhost -U postgres -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname='Housing_Price_postgres';" 2>&1

if ($checkDB -match "1") {
    Write-Host "WARNING: Database Housing_Price_postgres already exists" -ForegroundColor Yellow
} else {
    Write-Host "Creating database Housing_Price_postgres..." -ForegroundColor Blue
    $createDB = & $psqlPath -h localhost -U postgres -d postgres -c "CREATE DATABASE Housing_Price_postgres OWNER Housing_Price_postgres;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: Database created successfully" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to create database: $createDB" -ForegroundColor Red
    }
}

# Grant privileges
Write-Host "Setting user privileges..." -ForegroundColor Blue
$grantPrivileges = & $psqlPath -h localhost -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE Housing_Price_postgres TO Housing_Price_postgres;" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Privileges set successfully" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to set privileges: $grantPrivileges" -ForegroundColor Red
}

# Create .env file
Write-Host ""
Write-Host "Creating .env configuration file..." -ForegroundColor Blue

$envContent = @"
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Housing_Price_postgres
DB_USER=Housing_Price_postgres
DB_PASSWORD=123456

# Application Configuration
SECRET_KEY=your_secret_key_here_change_in_production
DEBUG=True
"@

try {
    Set-Content -Path ".env" -Value $envContent -Encoding UTF8
    Write-Host "SUCCESS: .env file created" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to create .env file: $($_.Exception.Message)" -ForegroundColor Red
}

# Clear password from environment
$env:PGPASSWORD = $null

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "PostgreSQL Setup Completed Successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Database Configuration:" -ForegroundColor Cyan
Write-Host "  Database Name: Housing_Price_postgres" -ForegroundColor Cyan
Write-Host "  Username: Housing_Price_postgres" -ForegroundColor Cyan
Write-Host "  Password: 123456" -ForegroundColor Cyan
Write-Host "  Host: localhost" -ForegroundColor Cyan
Write-Host "  Port: 5432" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Run database initialization: python init_database.py" -ForegroundColor Gray
Write-Host "2. Start the application: .\start_system.ps1" -ForegroundColor Gray
Write-Host ""

if (-not $SkipUserInput) {
    Write-Host "Press Enter to exit..." -ForegroundColor Gray
    Read-Host
}
