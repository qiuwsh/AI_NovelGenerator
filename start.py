#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI小说生成器启动脚本
自动检查依赖、配置环境并启动程序
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 9):
        print("错误: 需要Python 3.9或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)
    print(f"Python版本检查通过: {sys.version}")

def check_dependencies():
    """检查必需的依赖包"""
    required_packages = [
        'customtkinter',
        'langchain',
        'openai',
        'chromadb',
        'torch',
        'transformers'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    print("依赖检查通过")
    return True

def setup_logging():
    """设置日志配置"""
    import logging
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def create_directories():
    """创建必要的目录"""
    directories = [
        "logs",
        "vectorstore",
        "config_backups"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("目录结构检查完成")

def main():
    print("=== AI小说生成器启动检查 ===")
    
    # 检查Python版本
    check_python_version()
    
    # 检查依赖
    if not check_dependencies():
        input("按回车键退出...")
        sys.exit(1)
    
    # 设置环境
    setup_logging()
    create_directories()
    
    print("=== 启动主程序 ===")
    
    try:
        # 启动主程序
        from main import main as start_app
        start_app()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()