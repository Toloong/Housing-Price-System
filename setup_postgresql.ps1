# PostgreSQL 数据库设置脚本 (Windows PowerShell)
# 用于房价分析系统的用户管理功能

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "       PostgreSQL 数据库设置 (Windows)       " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# 检查PostgreSQL是否安装
Write-Host "检查PostgreSQL安装状态..." -ForegroundColor Yellow

$postgresqlInstalled = $false
$psqlPath = ""

# 常见的PostgreSQL安装路径
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

# 尝试从PATH中查找
if (-not $postgresqlInstalled) {
    try {
        $result = Get-Command psql -ErrorAction SilentlyContinue
        if ($result) {
            $psqlPath = $result.Source
            $postgresqlInstalled = $true
        }
    } catch {
        # psql不在PATH中
    }
}

if (-not $postgresqlInstalled) {
    Write-Host "❌ PostgreSQL未安装或未找到" -ForegroundColor Red
    Write-Host ""
    Write-Host "请下载并安装PostgreSQL:" -ForegroundColor Yellow
    Write-Host "1. 访问: https://www.postgresql.org/download/windows/" -ForegroundColor Cyan
    Write-Host "2. 下载PostgreSQL 12或更高版本" -ForegroundColor Cyan
    Write-Host "3. 运行安装程序，记住设置的postgres用户密码" -ForegroundColor Cyan
    Write-Host "4. 确保安装时勾选了'Stack Builder'和'Command Line Tools'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "安装完成后重新运行此脚本。" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "按任意键退出..." -ForegroundColor Gray
    Read-Host
    exit 1
}

Write-Host "✅ PostgreSQL已安装: $psqlPath" -ForegroundColor Green

# 检查PostgreSQL服务状态
Write-Host "检查PostgreSQL服务状态..." -ForegroundColor Yellow
$serviceStatus = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq "Running" }

if ($serviceStatus) {
    Write-Host "✅ PostgreSQL服务正在运行" -ForegroundColor Green
} else {
    Write-Host "⚠️  PostgreSQL服务未运行，尝试启动..." -ForegroundColor Yellow
    
    # 尝试启动服务
    $allPostgresServices = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    
    if ($allPostgresServices) {
        foreach ($service in $allPostgresServices) {
            try {
                Write-Host "启动服务: $($service.Name)" -ForegroundColor Blue
                Start-Service $service.Name -ErrorAction Stop
                Write-Host "✅ 服务启动成功" -ForegroundColor Green
                break
            } catch {
                Write-Host "❌ 服务启动失败: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "❌ 未找到PostgreSQL服务" -ForegroundColor Red
        Write-Host "请检查PostgreSQL是否正确安装" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "          数据库配置                        " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 获取postgres用户密码
Write-Host "请输入postgres用户的密码:" -ForegroundColor Yellow
Write-Host "(如果是首次安装，这是您在安装PostgreSQL时设置的密码)" -ForegroundColor Gray
$postgresPassword = Read-Host "postgres密码" -AsSecureString
$postgresPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($postgresPassword))

# 测试连接
Write-Host "测试数据库连接..." -ForegroundColor Yellow
$env:PGPASSWORD = $postgresPasswordPlain

try {
    $result = & $psqlPath -h localhost -U postgres -d postgres -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 数据库连接成功" -ForegroundColor Green
    } else {
        Write-Host "❌ 数据库连接失败" -ForegroundColor Red
        Write-Host "错误信息: $result" -ForegroundColor Red
        Write-Host ""
        Write-Host "可能的解决方案:" -ForegroundColor Yellow
        Write-Host "1. 确认postgres用户密码正确" -ForegroundColor Gray
        Write-Host "2. 确认PostgreSQL服务正在运行" -ForegroundColor Gray
        Write-Host "3. 检查防火墙设置" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "❌ 执行psql命令失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 创建应用数据库和用户
Write-Host ""
Write-Host "创建应用数据库和用户..." -ForegroundColor Blue

# 检查用户是否存在
Write-Host "检查用户 Housing_Price_postgres..." -ForegroundColor Yellow
$checkUser = & $psqlPath -h localhost -U postgres -d postgres -t -c "SELECT 1 FROM pg_roles WHERE rolname='Housing_Price_postgres';" 2>&1
if ($checkUser -match "1") {
    Write-Host "⚠️  用户 Housing_Price_postgres 已存在" -ForegroundColor Yellow
} else {
    Write-Host "创建用户 Housing_Price_postgres..." -ForegroundColor Blue
    $createUser = & $psqlPath -h localhost -U postgres -d postgres -c "CREATE USER Housing_Price_postgres WITH PASSWORD '123456';" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 用户创建成功" -ForegroundColor Green
    } else {
        Write-Host "❌ 用户创建失败: $createUser" -ForegroundColor Red
    }
}

# 检查数据库是否存在
Write-Host "检查数据库 Housing_Price_postgres..." -ForegroundColor Yellow
$checkDB = & $psqlPath -h localhost -U postgres -d postgres -t -c "SELECT 1 FROM pg_database WHERE datname='Housing_Price_postgres';" 2>&1
if ($checkDB -match "1") {
    Write-Host "⚠️  数据库 Housing_Price_postgres 已存在" -ForegroundColor Yellow
} else {
    Write-Host "创建数据库 Housing_Price_postgres..." -ForegroundColor Blue
    $createDB = & $psqlPath -h localhost -U postgres -d postgres -c "CREATE DATABASE Housing_Price_postgres OWNER Housing_Price_postgres;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 数据库创建成功" -ForegroundColor Green
    } else {
        Write-Host "❌ 数据库创建失败: $createDB" -ForegroundColor Red
    }
}

# 授予权限
Write-Host "设置用户权限..." -ForegroundColor Blue
$grantPrivileges = & $psqlPath -h localhost -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE Housing_Price_postgres TO Housing_Price_postgres;" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 权限设置成功" -ForegroundColor Green
} else {
    Write-Host "⚠️  权限设置可能失败: $grantPrivileges" -ForegroundColor Yellow
}

# 测试应用数据库连接
Write-Host ""
Write-Host "测试应用数据库连接..." -ForegroundColor Yellow
$env:PGPASSWORD = "123456"
$testConnection = & $psqlPath -h localhost -U Housing_Price_postgres -d Housing_Price_postgres -c "SELECT current_database(), current_user;" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 应用数据库连接成功" -ForegroundColor Green
    Write-Host "连接信息: $testConnection" -ForegroundColor Gray
} else {
    Write-Host "❌ 应用数据库连接失败: $testConnection" -ForegroundColor Red
}

# 清理环境变量
Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "          配置完成                          " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "数据库配置信息:" -ForegroundColor Green
Write-Host "  数据库名: Housing_Price_postgres" -ForegroundColor Cyan
Write-Host "  用户名: Housing_Price_postgres" -ForegroundColor Cyan
Write-Host "  密码: 123456" -ForegroundColor Cyan
Write-Host "  主机: localhost" -ForegroundColor Cyan
Write-Host "  端口: 5432" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "1. 运行数据库初始化脚本: python init_database.py" -ForegroundColor Gray
Write-Host "2. 启动应用系统: .\start_system.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
Read-Host
