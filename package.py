#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
项目打包脚本 - 用于创建可分享的项目包
"""

import os
import shutil
import zipfile
import tarfile
from pathlib import Path
import argparse

def create_package(output_dir="dist", package_name="new_energy_vehicle_analysis"):
    """
    创建项目包
    
    Args:
        output_dir: 输出目录
        package_name: 包名称
    """
    # 获取项目根目录
    project_root = Path(__file__).parent
    
    # 创建输出目录
    output_path = project_root / output_dir
    output_path.mkdir(exist_ok=True)
    
    # 创建临时目录
    temp_dir = output_path / package_name
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # 需要包含的文件和目录
    include_files = [
        "main.py",
        "run_example.py",
        "test_project.py",
        "requirements.txt",
        "README.md",
        "setup.py",
        ".gitignore"
    ]
    
    include_dirs = [
        "src",
        "config",
        "data/sample",  # 只包含示例数据
        "docs"  # 文档目录
    ]
    
    # 复制文件
    for file_name in include_files:
        src_file = project_root / file_name
        if src_file.exists():
            dst_file = temp_dir / file_name
            shutil.copy2(src_file, dst_file)
            print(f"复制文件: {file_name}")
    
    # 复制目录
    for dir_name in include_dirs:
        src_dir = project_root / dir_name
        if src_dir.exists():
            dst_dir = temp_dir / dir_name
            shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))
            print(f"复制目录: {dir_name}")
    
    # 创建示例数据目录
    sample_data_dir = temp_dir / "data" / "sample"
    sample_data_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制示例数据文件
    sample_files = [
        "gdp.csv",
        "cpi.csv",
        "2新能源汽车分厂商产销(207家厂商，201812-202210月度数据).csv"
    ]
    
    data_dir = project_root.parent / "数据"
    for file_name in sample_files:
        src_file = data_dir / file_name
        if src_file.exists():
            dst_file = sample_data_dir / file_name
            shutil.copy2(src_file, dst_file)
            print(f"复制示例数据: {file_name}")
    
    # 创建环境变量模板
    env_template = temp_dir / ".env.template"
    with open(env_template, 'w', encoding='utf-8') as f:
        f.write("# 环境变量配置模板\n")
        f.write("# 复制此文件为 .env 并填入实际值\n\n")
        f.write("# 硅基流动API密钥\n")
        f.write("SILICONFLOW_API_KEY=your_api_key_here\n\n")
        f.write("# 数据根目录路径\n")
        f.write("DATA_ROOT_PATH=./data\n\n")
        f.write("# 日志级别\n")
        f.write("LOG_LEVEL=INFO\n")
    
    # 创建安装脚本
    install_script = temp_dir / "install.sh"
    with open(install_script, 'w', encoding='utf-8') as f:
        f.write("#!/bin/bash\n")
        f.write("# 安装脚本\n\n")
        f.write("echo '正在安装新能源汽车行业分析系统...'\n\n")
        f.write("# 检查Python版本\n")
        f.write("python3 --version\n\n")
        f.write("# 创建虚拟环境\n")
        f.write("python3 -m venv venv\n")
        f.write("source venv/bin/activate\n\n")
        f.write("# 安装依赖\n")
        f.write("pip install -r requirements.txt\n\n")
        f.write("# 创建环境变量文件\n")
        f.write("cp .env.template .env\n")
        f.write("echo '请编辑 .env 文件，填入您的API密钥'\n\n")
        f.write("echo '安装完成！'\n")
        f.write("echo '运行 ./run_example.py 开始使用'\n")
    
    # 创建Windows安装脚本
    install_script_win = temp_dir / "install.bat"
    with open(install_script_win, 'w', encoding='utf-8') as f:
        f.write("@echo off\n")
        f.write("REM 安装脚本\n\n")
        f.write("echo 正在安装新能源汽车行业分析系统...\n\n")
        f.write("REM 检查Python版本\n")
        f.write("python --version\n\n")
        f.write("REM 创建虚拟环境\n")
        f.write("python -m venv venv\n")
        f.write("call venv\\Scripts\\activate.bat\n\n")
        f.write("REM 安装依赖\n")
        f.write("pip install -r requirements.txt\n\n")
        f.write("REM 创建环境变量文件\n")
        f.write("copy .env.template .env\n")
        f.write("echo 请编辑 .env 文件，填入您的API密钥\n\n")
        f.write("echo 安装完成！\n")
        f.write("echo 运行 python run_example.py 开始使用\n")
        f.write("pause\n")
    
    # 设置执行权限
    os.chmod(install_script, 0o755)
    
    # 创建ZIP包
    zip_path = output_path / f"{package_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in temp_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(temp_dir)
                zipf.write(file_path, arcname)
    
    # 创建TAR包
    tar_path = output_path / f"{package_name}.tar.gz"
    with tarfile.open(tar_path, 'w:gz') as tarf:
        tarf.add(temp_dir, arcname=package_name)
    
    # 清理临时目录
    shutil.rmtree(temp_dir)
    
    print(f"\n打包完成！")
    print(f"ZIP包: {zip_path}")
    print(f"TAR包: {tar_path}")
    
    return zip_path, tar_path

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="创建项目分享包")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="dist",
        help="输出目录"
    )
    parser.add_argument(
        "--package-name",
        type=str,
        default="new_energy_vehicle_analysis",
        help="包名称"
    )
    
    args = parser.parse_args()
    
    create_package(args.output_dir, args.package_name)

if __name__ == "__main__":
    main()