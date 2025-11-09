@echo off
REM Docker部署脚本 (Windows版本)

setlocal enabledelayedexpansion

REM 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

echo [INFO] Docker环境检查通过

REM 检查环境变量文件
if not exist ".env" (
    echo [WARNING] .env文件不存在，正在创建模板文件...
    copy .env.template .env >nul
    echo [WARNING] 请编辑 .env 文件，填入您的API密钥
    echo [WARNING] 编辑完成后，重新运行此脚本
    pause
    exit /b 1
)

REM 检查API密钥是否已设置
findstr /C:"your_api_key_here" .env >nul
if %errorlevel% equ 0 (
    echo [ERROR] 请在 .env 文件中设置您的API密钥
    pause
    exit /b 1
)

echo [INFO] 环境变量检查通过

REM 创建必要的目录
echo [INFO] 创建必要的目录...
if not exist "data" mkdir data
if not exist "output" mkdir output
if not exist "logs" mkdir logs
echo [INFO] 目录创建完成

REM 处理命令行参数
if "%1"=="stop" (
    echo [INFO] 停止容器...
    docker-compose down
    echo [INFO] 容器已停止
    goto :end
)

if "%1"=="restart" (
    echo [INFO] 重启容器...
    docker-compose restart
    echo [INFO] 容器已重启
    goto :end
)

if "%1"=="logs" (
    docker-compose logs -f new-energy-analysis
    goto :end
)

if "%1"=="status" (
    echo [INFO] 容器状态：
    docker-compose ps
    goto :end
)

if "%1"=="help" goto :show_usage
if "%1"=="-h" goto :show_usage
if "%1"=="--help" goto :show_usage

REM 主部署流程
echo [INFO] 开始部署新能源汽车行业分析系统...

echo [INFO] 构建Docker镜像...
docker-compose build
if %errorlevel% neq 0 (
    echo [ERROR] Docker镜像构建失败
    pause
    exit /b 1
)
echo [INFO] Docker镜像构建完成

echo [INFO] 启动容器...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] 容器启动失败
    pause
    exit /b 1
)
echo [INFO] 容器启动完成

echo [INFO] 容器状态：
docker-compose ps

goto :show_usage

:show_usage
echo.
echo [INFO] 使用说明：
echo 1. 运行完整分析：
echo    docker-compose exec new-energy-analysis python main.py
echo.
echo 2. 运行示例：
echo    docker-compose exec new-energy-analysis python run_example.py
echo.
echo 3. 查看日志：
echo    docker-compose logs -f new-energy-analysis
echo.
echo 4. 停止容器：
echo    docker-compose down
echo.
echo 5. 查看输出结果：
echo    dir output\
echo.
echo [INFO] 部署完成！

:end
pause