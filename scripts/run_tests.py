#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试执行脚本
"""
import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到系统路径
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


def run_tests():
    """执行单元测试"""
    print("=" * 60)
    print("开始执行单元测试...")
    print("=" * 60)
    
    # 运行测试
    result = subprocess.run(
        ["python", "-m", "pytest"],
        cwd=PROJECT_ROOT
    )
    
    if result.returncode != 0:
        print("测试失败")
        return False
    
    print("所有测试通过")
    return True


def run_format():
    """执行代码格式化"""
    print("=" * 60)
    print("开始格式化代码...")
    print("=" * 60)
    
    # 运行black格式化
    subprocess.run(
        ["python", "-m", "black", "src", "tests", "scripts"],
        cwd=PROJECT_ROOT
    )
    
    # 运行isort格式化
    subprocess.run(
        ["python", "-m", "isort", "src", "tests", "scripts"],
        cwd=PROJECT_ROOT
    )
    
    print("代码格式化完成")


def run_type_check():
    """执行类型检查"""
    print("=" * 60)
    print("开始类型检查...")
    print("=" * 60)
    
    # 运行mypy类型检查
    result = subprocess.run(
        ["python", "-m", "mypy", "src"],
        cwd=PROJECT_ROOT
    )
    
    if result.returncode != 0:
        print("类型检查发现问题")
        return False
    
    print("类型检查通过")
    return True


def main():
    """主函数"""
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description="项目工具脚本")
    parser.add_argument("command", choices=["test", "format", "typecheck", "all"], 
                        help="要执行的命令")
    args = parser.parse_args()
    
    # 执行命令
    if args.command == "test":
        run_tests()
    elif args.command == "format":
        run_format()
    elif args.command == "typecheck":
        run_type_check()
    elif args.command == "all":
        run_format()
        type_check_result = run_type_check()
        test_result = run_tests()
        
        if not type_check_result or not test_result:
            sys.exit(1)


if __name__ == "__main__":
    main() 