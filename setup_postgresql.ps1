# PostgreSQL Database Setup Script for Housing Price Analysis System
# Unified version with UTF-8 encoding support and error handling

param(
    [string]$PostgresPassword = "",
    [switch]$SkipUserInput
)

# Set encoding to UTF-8 to avoid character encoding issues
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Clear screen and show header
Clear-Host
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Database Setup" -ForegroundColor Cyan
Write-Host "Housing Price Analysis System v3.0" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Function to write colored status messages
function Write-Status {
    param(
        [string]$Message,
        [string]$Status = "INFO"
    )
    
    switch ($Status) {
        "SUCCESS" { Write-Host "SUCCESS: $Message" -ForegroundColor Green }
        "ERROR" { Write-Host "ERROR: $Message" -ForegroundColor Red }
        "WARNING" { Write-Host "WARNING: $Message" -ForegroundColor Yellow }
        "INFO" { Write-Host "INFO: $Message" -ForegroundColor Blue }
        default { Write-Host $Message -ForegroundColor Gray }
    }
}

# Check PostgreSQL installation
Write-Status "Checking PostgreSQL installation..." "INFO"

$postgresqlInstalled = $false
$psqlPath = ""

# Common PostgreSQL installation paths
$commonPaths = @(
    "C:\Program Files\PostgreSQL\*\bin\psql.exe",
    "C:\Program Files (x86)\PostgreSQL\*\bin\psql.exe",
    "C:\PostgreSQL\*\bin\psql.exe"
)

# Search for PostgreSQL in common paths
foreach ($path in $commonPaths) {
    $found = Get-ChildItem $path -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $psqlPath = $found.FullName
        $postgresqlInstalled = $true
        break
    }
}

# Try to find in PATH environment variable
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

# Exit if PostgreSQL not found
if (-not $postgresqlInstalled) {
    Write-Status "PostgreSQL not installed or not found in PATH" "ERROR"
    Write-Host ""
    Write-Host "Please install PostgreSQL:" -ForegroundColor Yellow
    Write-Host "1. Visit: https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
    Write-Host "2. Download PostgreSQL 12 or higher" -ForegroundColor Cyan
    Write-Host "3. Remember the postgres user password during installation" -ForegroundColor Cyan
    Write-Host "4. Add PostgreSQL bin directory to PATH" -ForegroundColor Cyan
    Write-Host "5. Re-run this script after installation" -ForegroundColor Cyan
    Write-Host ""
    if (-not $SkipUserInput) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

Write-Status "PostgreSQL found at: $psqlPath" "SUCCESS"

# Get postgres password if not provided
if ([string]::IsNullOrEmpty($PostgresPassword) -and -not $SkipUserInput) {
    Write-Host ""
    $securePassword = Read-Host "Enter postgres user password" -AsSecureString
    $PostgresPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword))
}

if ([string]::IsNullOrEmpty($PostgresPassword)) {
    Write-Status "Password is required for database setup" "ERROR"
    if (-not $SkipUserInput) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Set environment variable for password (temporary)
$env:PGPASSWORD = $PostgresPassword

# Test PostgreSQL connection
Write-Host ""
Write-Status "Testing PostgreSQL connection..." "INFO"

try {
    $testConnection = & $psqlPath -h localhost -U postgres -d postgres -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Cannot connect to PostgreSQL with provided password" "ERROR"
        Write-Host "Error details: $testConnection" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please check:" -ForegroundColor Yellow
        Write-Host "1. PostgreSQL service is running" -ForegroundColor Cyan
        Write-Host "2. Password is correct" -ForegroundColor Cyan
        Write-Host "3. User postgres exists and has login permission" -ForegroundColor Cyan
        $env:PGPASSWORD = $null
        if (-not $SkipUserInput) {
            Read-Host "Press Enter to exit"
        }
        exit 1
    }
    Write-Status "Connected to PostgreSQL successfully" "SUCCESS"
} catch {
    Write-Status "Failed to execute psql command: $($_.Exception.Message)" "ERROR"
    $env:PGPASSWORD = $null
    if (-not $SkipUserInput) {
        Read-Host "Press Enter to exit"
    }
    exit 1
}

# Create application database and user
Write-Host ""
Write-Status "Setting up application database and user..." "INFO"

# Check if user exists
Write-Status "Checking user Housing_Price_postgres..." "INFO"
$checkUser = & $psqlPath -h localhost -U postgres -d postgres -t -c "SELECT 1 FROM pg_roles WHERE rolname='Housing_Price_postgres';" 2>&1

if ($checkUser -match "1") {
    Write-Status "User Housing_Price_postgres already exists" "WARNING"
} else {
    Write-Status "Creating user Housing_Price_postgres..." "INFO"
    $createUser = & $psqlPath -h localhost -U postgres -d postgres -c "CREATE USER Housing_Price_postgres WITH PASSWORD '123456';" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Status "User created successfully" "SUCCESS"
    } else {
        Write-Status "Failed to create user: $createUser" "ERROR"
        $env:PGPASSWORD = $null
        if (-not $SkipUserInput) {
            Read-Host "Press Enter to exit"
        }
        exit 1
    }
}

# Check if database exists
Write-Status "Checking database Housing_Price_postgres..." "INFO"
$checkDB = & $psqlPath -h localhost -U postgres -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname='Housing_Price_postgres';" 2>&1

if ($checkDB -match "1") {
    Write-Status "Database Housing_Price_postgres already exists" "WARNING"
} else {
    Write-Status "Creating database Housing_Price_postgres..." "INFO"
    $createDB = & $psqlPath -h localhost -U postgres -d postgres -c "CREATE DATABASE Housing_Price_postgres OWNER Housing_Price_postgres;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Status "Database created successfully" "SUCCESS"
    } else {
        Write-Status "Failed to create database: $createDB" "ERROR"
        $env:PGPASSWORD = $null
        if (-not $SkipUserInput) {
            Read-Host "Press Enter to exit"
        }
        exit 1
    }
}

# Grant privileges
Write-Status "Setting user privileges..." "INFO"
$grantPrivileges = & $psqlPath -h localhost -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE Housing_Price_postgres TO Housing_Price_postgres;" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Status "Privileges set successfully" "SUCCESS"
} else {
    Write-Status "Failed to set privileges: $grantPrivileges" "WARNING"
}

# Create .env file if it doesn't exist
Write-Host ""
Write-Status "Creating .env configuration file..." "INFO"

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
    if (-not (Test-Path ".env")) {
        Set-Content -Path ".env" -Value $envContent -Encoding UTF8
        Write-Status ".env file created successfully" "SUCCESS"
    } else {
        Write-Status ".env file already exists, skipping creation" "INFO"
    }
} catch {
    Write-Status "Failed to create .env file: $($_.Exception.Message)" "ERROR"
}

# Clear password from environment for security
$env:PGPASSWORD = $null

# Show completion message
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "PostgreSQL Setup Completed Successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Database Configuration:" -ForegroundColor Cyan
Write-Host "  Database Name: Housing_Price_postgres" -ForegroundColor White
Write-Host "  Username: Housing_Price_postgres" -ForegroundColor White
Write-Host "  Password: 123456" -ForegroundColor White
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: 5432" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Initialize database tables: python init_database.py" -ForegroundColor Gray
Write-Host "2. Start the application: .\start_system.bat" -ForegroundColor Gray
Write-Host ""

if (-not $SkipUserInput) {
    Write-Host "Press Enter to exit..." -ForegroundColor Gray
    Read-Host
}
