#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
新能源汽车行业Agent分析系统示例运行脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并打印输出"""
    print(f"执行命令: {cmd}")
    result = subprocess.run(
        cmd, 
        shell=True, 
        cwd=cwd, 
        capture_output=True, 
        text=True
    )
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(f"错误: {result.stderr}")
    
    return result.returncode == 0

def main():
    """主函数"""
    project_root = Path(__file__).parent
    
    print("="*50)
    print("新能源汽车行业Agent分析系统 - 示例运行")
    print("="*50)
    
    # 检查Python版本
    print("\n1. 检查Python版本...")
    python_version = sys.version
    print(f"Python版本: {python_version}")
    
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        return False
    
    # 安装依赖
    print("\n2. 安装依赖...")
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", cwd=project_root):
        print("错误: 依赖安装失败")
        return False
    
    # 检查环境变量文件
    print("\n3. 检查环境变量文件...")
    env_file = project_root / ".env"
    if not env_file.exists():
        print("错误: 环境变量文件.env不存在")
        return False
    
    # 检查API密钥
    print("\n4. 检查API密钥...")
    with open(env_file, 'r') as f:
        env_content = f.read()
        if "SILICONFLOW_API_KEY" not in env_content:
            print("警告: 未找到SILICONFLOW_API_KEY环境变量")
        else:
            print("API密钥配置正常")
    
    # 检查数据目录
    print("\n5. 检查数据目录...")
    data_root = project_root.parent / "数据"
    if not data_root.exists():
        print(f"警告: 数据目录不存在: {data_root}")
    else:
        print(f"数据目录: {data_root}")
        
        # 列出数据文件
        data_files = list(data_root.glob("*.csv"))
        if data_files:
            print("找到以下数据文件:")
            for file in data_files[:5]:  # 只显示前5个
                print(f"- {file.name}")
            if len(data_files) > 5:
                print(f"... 还有{len(data_files)-5}个文件")
        else:
            print("警告: 未找到CSV数据文件")
    
    # 运行示例分析
    print("\n6. 运行示例分析...")
    cmd = f"{sys.executable} main.py --focus 市场 财务 --no-charts"
    if not run_command(cmd, cwd=project_root):
        print("错误: 示例分析运行失败")
        return False
    
    print("\n示例运行完成!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)