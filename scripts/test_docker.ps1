# Docker 测试脚本
# 用于验证 Docker 安装和项目配置

Write-Host "=== Docker 安装测试 ===" -ForegroundColor Cyan

# 测试 1: 检查 Docker 是否安装
Write-Host "`n[Test 1] 检查 Docker 版本..." -ForegroundColor Yellow
try {
    docker --version
    Write-Host "✅ Docker 已安装" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker 未安装或未在 PATH 中" -ForegroundColor Red
    exit 1
}

# 测试 2: 检查 Docker Compose
Write-Host "`n[Test 2] 检查 Docker Compose..." -ForegroundColor Yellow
try {
    docker-compose --version
    Write-Host "✅ Docker Compose 已安装" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose 未安装" -ForegroundColor Red
}

# 测试 3: 检查 Docker 守护进程
Write-Host "`n[Test 3] 检查 Docker 守护进程..." -ForegroundColor Yellow
try {
    docker info | Select-String "Server Version"
    Write-Host "✅ Docker 守护进程运行中" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker 守护进程未运行" -ForegroundColor Red
    Write-Host "提示: 请启动 Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# 测试 4: 验证 Dockerfile 语法
Write-Host "`n[Test 4] 验证 Dockerfile 语法..." -ForegroundColor Yellow
if (Test-Path "Dockerfile") {
    Write-Host "✅ Dockerfile 存在" -ForegroundColor Green
    
    # 尝试构建（不使用缓存，仅验证）
    Write-Host "开始构建 Docker 镜像（测试模式）..." -ForegroundColor Cyan
    docker build --target development -t matformppo:test . --no-cache
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dockerfile 构建成功" -ForegroundColor Green
        
        # 清理测试镜像
        Write-Host "清理测试镜像..." -ForegroundColor Yellow
        docker rmi matformppo:test
    } else {
        Write-Host "❌ Dockerfile 构建失败" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Dockerfile 不存在" -ForegroundColor Red
    exit 1
}

# 测试 5: 验证 docker-compose.yml
Write-Host "`n[Test 5] 验证 docker-compose.yml..." -ForegroundColor Yellow
if (Test-Path "docker-compose.yml") {
    Write-Host "✅ docker-compose.yml 存在" -ForegroundColor Green
    
    # 验证配置
    docker-compose config --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ docker-compose.yml 配置有效" -ForegroundColor Green
    } else {
        Write-Host "❌ docker-compose.yml 配置无效" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ docker-compose.yml 不存在" -ForegroundColor Red
    exit 1
}

# 测试 6: 检查 .env 文件
Write-Host "`n[Test 6] 检查环境配置..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env 文件存在" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env 文件不存在" -ForegroundColor Yellow
    Write-Host "提示: 请从 .env.example 复制创建 .env 文件" -ForegroundColor Yellow
}

# 测试 7: 测试完整构建流程
Write-Host "`n[Test 7] 测试完整 Docker Compose 构建..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟时间..." -ForegroundColor Cyan

docker-compose build training

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker Compose 构建成功" -ForegroundColor Green
} else {
    Write-Host "❌ Docker Compose 构建失败" -ForegroundColor Red
    exit 1
}

# 最终总结
Write-Host "`n=== 测试完成 ===" -ForegroundColor Cyan
Write-Host "✅ 所有 Docker 配置测试通过！" -ForegroundColor Green
Write-Host "`n下一步可以运行:" -ForegroundColor Yellow
Write-Host "  docker-compose up training    # 启动训练服务" -ForegroundColor White
Write-Host "  docker-compose up dashboard   # 启动仪表盘" -ForegroundColor White
Write-Host "  docker-compose up test        # 运行测试" -ForegroundColor White
