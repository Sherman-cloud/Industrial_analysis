#!/bin/bash

# Docker部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    print_message "Docker环境检查通过"
}

# 检查环境变量文件
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env文件不存在，正在创建模板文件..."
        cp .env.template .env
        print_warning "请编辑 .env 文件，填入您的API密钥"
        print_warning "编辑完成后，重新运行此脚本"
        exit 1
    fi
    
    # 检查API密钥是否已设置
    if grep -q "your_api_key_here" .env; then
        print_error "请在 .env 文件中设置您的API密钥"
        exit 1
    fi
    
    print_message "环境变量检查通过"
}

# 创建必要的目录
create_directories() {
    print_message "创建必要的目录..."
    mkdir -p data output logs
    print_message "目录创建完成"
}

# 构建Docker镜像
build_image() {
    print_message "构建Docker镜像..."
    docker-compose build
    print_message "Docker镜像构建完成"
}

# 启动容器
start_container() {
    print_message "启动容器..."
    docker-compose up -d
    print_message "容器启动完成"
}

# 显示容器状态
show_status() {
    print_message "容器状态："
    docker-compose ps
}

# 显示使用说明
show_usage() {
    print_message "使用说明："
    echo "1. 运行完整分析："
    echo "   docker-compose exec new-energy-analysis python main.py"
    echo ""
    echo "2. 运行示例："
    echo "   docker-compose exec new-energy-analysis python run_example.py"
    echo ""
    echo "3. 查看日志："
    echo "   docker-compose logs -f new-energy-analysis"
    echo ""
    echo "4. 停止容器："
    echo "   docker-compose down"
    echo ""
    echo "5. 查看输出结果："
    echo "   ls -la output/"
}

# 主函数
main() {
    print_message "开始部署新能源汽车行业分析系统..."
    
    check_docker
    check_env_file
    create_directories
    build_image
    start_container
    show_status
    show_usage
    
    print_message "部署完成！"
}

# 处理命令行参数
case "${1:-}" in
    "stop")
        print_message "停止容器..."
        docker-compose down
        print_message "容器已停止"
        ;;
    "restart")
        print_message "重启容器..."
        docker-compose restart
        print_message "容器已重启"
        ;;
    "logs")
        docker-compose logs -f new-energy-analysis
        ;;
    "status")
        show_status
        ;;
    "help"|"-h"|"--help")
        echo "用法: $0 [命令]"
        echo ""
        echo "命令:"
        echo "  (无参数)  部署系统"
        echo "  stop      停止容器"
        echo "  restart   重启容器"
        echo "  logs      查看日志"
        echo "  status    查看状态"
        echo "  help      显示帮助"
        ;;
    "")
        main
        ;;
    *)
        print_error "未知命令: $1"
        echo "使用 '$0 help' 查看帮助"
        exit 1
        ;;
esac