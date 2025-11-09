#!/usr/bin/env python3
"""
项目打包脚本
用于将项目打包为可分享的压缩文件
"""

import os
import zipfile
import shutil
from datetime import datetime

def create_package():
    """创建项目包"""
    # 定义包名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"new-energy-analysis-{timestamp}"
    package_dir = f"temp_{package_name}"
    package_file = f"{package_name}.zip"
    
    # 创建临时目录
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # 需要包含的文件和目录
    include_items = [
        "src", "config", "requirements.txt", "main.py", "run_example.py", 
        "test_project.py", ".env.template", "Dockerfile", "docker-compose.yml",
        "deploy-docker.sh", "deploy-docker.bat", ".dockerignore", "LICENSE",
        "docs", "example_data"
    ]
    
    # 复制文件和目录
    for item in include_items:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(package_dir, item))
            else:
                shutil.copy2(item, package_dir)
    
    # 创建README.md
    readme_content = f"""# 新能源汽车行业分析系统

## 快速开始

1. 解压此压缩包到目标目录
2. 配置环境变量：
   ```bash
   # 复制环境变量模板
   cp .env.template .env
   
   # 编辑.env文件，设置API密钥
   nano .env
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 运行分析：
   ```bash
   python main.py
   ```

## Docker部署

```bash
# 配置环境变量后
docker-compose up -d
```

## 更多信息

- 详细安装说明：docs/INSTALLATION.md
- Docker部署指南：docs/DOCKER_DEPLOYMENT.md
- 项目分享指南：docs/SHARING_GUIDE.md
- 示例数据说明：example_data/README.md

## 许可证

MIT License - 详见LICENSE文件
"""
    
    with open(os.path.join(package_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    # 创建ZIP文件
    with zipfile.ZipFile(package_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arcname)
    
    # 清理临时目录
    shutil.rmtree(package_dir)
    
    print(f"✅ 项目包已创建: {package_file}")
    print(f"📦 包大小: {os.path.getsize(package_file) / 1024 / 1024:.2f} MB")
    print("\n📋 分享说明:")
    print("1. 将此ZIP文件发送给其他人")
    print("2. 接收者解压后按照README.md中的说明进行配置和运行")
    print("3. 如需Docker部署，请确保接收者已安装Docker环境")

if __name__ == "__main__":
    create_package()