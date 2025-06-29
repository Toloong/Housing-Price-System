# 房价分析系统一键启动脚本 (Windows PowerShell)
# 运行前请确保已安装Python 3.8+和PostgreSQL

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "        房价分析系统 Windows 启动脚本         " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# 检查Python是否安装
Write-Host "检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python已安装: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python未安装，请先安装Python 3.8+" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Python未安装，请先安装Python 3.8+" -ForegroundColor Red
    exit 1
}

# 检查虚拟环境
Write-Host "检查虚拟环境..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "✅ 虚拟环境已存在" -ForegroundColor Green
} else {
    Write-Host "📦 创建虚拟环境..." -ForegroundColor Blue
    python -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 虚拟环境创建成功" -ForegroundColor Green
    } else {
        Write-Host "❌ 虚拟环境创建失败" -ForegroundColor Red
        exit 1
    }
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  执行策略问题，尝试临时设置..." -ForegroundColor Yellow
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
    & ".\.venv\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 虚拟环境激活失败" -ForegroundColor Red
        Write-Host "请手动运行: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process" -ForegroundColor Yellow
        exit 1
    }
}
Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green

# 安装依赖
Write-Host "检查依赖包..." -ForegroundColor Yellow
$needInstall = $false
try {
    python -c "import fastapi, uvicorn, streamlit" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $needInstall = $true
    }
} catch {
    $needInstall = $true
}

if ($needInstall) {
    Write-Host "📦 安装依赖包..." -ForegroundColor Blue
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 依赖包安装成功" -ForegroundColor Green
    } else {
        Write-Host "❌ 依赖包安装失败" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ 依赖包已安装" -ForegroundColor Green
}

# 检查PostgreSQL连接（可选）
Write-Host "检查数据库连接..." -ForegroundColor Yellow
$dbConnected = $false
try {
    python -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://Housing_Price_postgres:123456@localhost/Housing_Price_postgres')
    conn.close()
    print('connected')
except:
    print('failed')
" 2>$null | ForEach-Object {
        if ($_ -eq "connected") {
            $dbConnected = $true
        }
    }
} catch {
    # 数据库连接失败
}

if ($dbConnected) {
    Write-Host "✅ 数据库连接正常" -ForegroundColor Green
} else {
    Write-Host "⚠️  数据库连接失败，用户管理功能将不可用" -ForegroundColor Yellow
    Write-Host "   如需使用用户管理功能，请运行: python init_database.py" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "          系统启动                         " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 询问启动方式
Write-Host "请选择启动方式:" -ForegroundColor White
Write-Host "1. 自动启动 (推荐) - 自动打开新窗口启动前后端" -ForegroundColor Green
Write-Host "2. 仅启动后端 - 手动在另一个终端启动前端" -ForegroundColor Yellow
Write-Host "3. 仅启动前端 - 需要后端已在运行" -ForegroundColor Yellow
Write-Host "4. 退出" -ForegroundColor Red

$choice = Read-Host "请输入选择 (1-4)"

switch ($choice) {
    "1" {
        Write-Host "🚀 自动启动前后端..." -ForegroundColor Green
        Write-Host ""
        Write-Host "启动后端服务..." -ForegroundColor Blue
        
        # 启动后端 - 在新窗口中
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "
            Set-Location '$PWD';
            .\.venv\Scripts\Activate.ps1;
            Write-Host '🔧 后端服务启动中...' -ForegroundColor Blue;
            Write-Host '访问地址: http://localhost:8000' -ForegroundColor Green;
            Write-Host 'API文档: http://localhost:8000/docs' -ForegroundColor Green;
            Write-Host '';
            uvicorn backend.main:app --reload --port 8000
        "
        
        # 等待后端启动
        Write-Host "等待后端启动..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
        
        Write-Host "启动前端应用..." -ForegroundColor Blue
        
        # 启动前端 - 在新窗口中
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "
            Set-Location '$PWD';
            .\.venv\Scripts\Activate.ps1;
            Write-Host '🎨 前端应用启动中...' -ForegroundColor Blue;
            Write-Host '应用将在浏览器中自动打开' -ForegroundColor Green;
            Write-Host '访问地址: http://localhost:8501' -ForegroundColor Green;
            Write-Host '';
            streamlit run frontend/app.py
        "
        
        Write-Host ""
        Write-Host "✅ 系统启动完成!" -ForegroundColor Green
        Write-Host "前端应用: http://localhost:8501" -ForegroundColor Cyan
        Write-Host "后端API: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "按任意键关闭此窗口..." -ForegroundColor Gray
        Read-Host
    }
    
    "2" {
        Write-Host "🔧 启动后端服务..." -ForegroundColor Blue
        Write-Host "访问地址: http://localhost:8000" -ForegroundColor Green
        Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Green
        Write-Host ""
        Write-Host "请在另一个终端运行前端:"
        Write-Host "  .\.venv\Scripts\activate" -ForegroundColor Yellow
        Write-Host "  streamlit run frontend/app.py" -ForegroundColor Yellow
        Write-Host ""
        uvicorn backend.main:app --reload --port 8000
    }
    
    "3" {
        Write-Host "🎨 启动前端应用..." -ForegroundColor Blue
        Write-Host "应用将在浏览器中自动打开" -ForegroundColor Green
        Write-Host ""
        streamlit run frontend/app.py
    }
    
    "4" {
        Write-Host "👋 退出启动脚本" -ForegroundColor Yellow
        exit 0
    }
    
    default {
        Write-Host "❌ 无效选择，退出" -ForegroundColor Red
        exit 1
    }
}
