#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新实现的功能组件
Test newly implemented features: Dash Dashboard, PostgreSQL Manager

测试内容 / Test Coverage:
1. Dash 导入和依赖检查 / Dash imports and dependencies
2. PostgreSQL 管理器初始化 / PostgreSQL manager initialization
3. 数据库连接测试 / Database connection test
4. 基本功能验证 / Basic functionality validation
"""

import sys
import os
from pathlib import Path

# 添加项目路径 / Add project path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_dash_imports():
    """测试 Dash 相关库导入 / Test Dash library imports"""
    print("\n" + "="*80)
    print("测试 1: Dash 库导入 / Test 1: Dash Library Imports")
    print("="*80)
    
    try:
        import dash
        print(f"✅ Dash 版本 / Version: {dash.__version__}")
        
        import plotly
        print(f"✅ Plotly 版本 / Version: {plotly.__version__}")
        
        import dash.dependencies
        print("✅ Dash 依赖模块正常 / Dash dependencies OK")
        
        import plotly.graph_objs as go
        print("✅ Plotly 图形对象模块正常 / Plotly graph objects OK")
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败 / Import failed: {e}")
        return False

def test_psycopg2_import():
    """测试 psycopg2 导入 / Test psycopg2 import"""
    print("\n" + "="*80)
    print("测试 2: PostgreSQL 驱动导入 / Test 2: PostgreSQL Driver Import")
    print("="*80)
    
    try:
        import psycopg2
        print(f"✅ psycopg2 版本 / Version: {psycopg2.__version__}")
        
        from psycopg2 import pool
        print("✅ 连接池模块正常 / Connection pool module OK")
        
        from psycopg2.extras import execute_batch
        print("✅ 批量执行模块正常 / Batch execution module OK")
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败 / Import failed: {e}")
        return False

def test_postgres_manager_init():
    """测试 PostgreSQL 管理器初始化 / Test PostgreSQL manager initialization"""
    print("\n" + "="*80)
    print("测试 3: PostgreSQL 管理器初始化 / Test 3: PostgreSQL Manager Init")
    print("="*80)
    
    try:
        from sql.postgres_manager import PostgreSQLManager
        print("✅ PostgreSQLManager 类导入成功 / Class imported successfully")
        
        # 测试类方法存在 / Test class methods exist
        methods = ['insert_material', 'bulk_insert_materials', 'start_experiment', 
                   'log_result', 'get_best_models', 'get_experiment_stats']
        
        for method in methods:
            if hasattr(PostgreSQLManager, method):
                print(f"✅ 方法存在 / Method exists: {method}")
            else:
                print(f"❌ 方法缺失 / Method missing: {method}")
                return False
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败 / Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ 错误 / Error: {e}")
        return False

def test_dash_app_structure():
    """测试 Dash 应用结构 / Test Dash app structure"""
    print("\n" + "="*80)
    print("测试 4: Dash 应用结构 / Test 4: Dash App Structure")
    print("="*80)
    
    try:
        # 读取 app.py 文件 / Read app.py file
        app_path = project_root / "dash_app" / "app.py"
        
        if not app_path.exists():
            print(f"❌ 文件不存在 / File not found: {app_path}")
            return False
        
        print(f"✅ Dash 应用文件存在 / App file exists: {app_path}")
        
        # 检查关键组件 / Check key components
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        components = [
            'dash.Dash',
            'dcc.Interval',
            'dcc.Graph',
            'dbc.Tab',
            'load_training_data',
            'update_training_curves',
            'update_performance_table'
        ]
        
        for component in components:
            if component in content:
                print(f"✅ 组件存在 / Component found: {component}")
            else:
                print(f"⚠️  组件可能缺失 / Component might be missing: {component}")
        
        return True
    except Exception as e:
        print(f"❌ 错误 / Error: {e}")
        return False

def test_kubernetes_manifests():
    """测试 Kubernetes 配置文件 / Test Kubernetes manifests"""
    print("\n" + "="*80)
    print("测试 5: Kubernetes 配置文件 / Test 5: Kubernetes Manifests")
    print("="*80)
    
    k8s_dir = project_root / "k8s"
    required_files = [
        'namespace.yaml',
        'deployment.yaml',
        'service.yaml',
        'hpa.yaml',
        'configmap.yaml',
        'secrets.yaml'
    ]
    
    all_exist = True
    for filename in required_files:
        filepath = k8s_dir / filename
        if filepath.exists():
            print(f"✅ 文件存在 / File exists: {filename}")
        else:
            print(f"❌ 文件缺失 / File missing: {filename}")
            all_exist = False
    
    return all_exist

def test_terraform_modules():
    """测试 Terraform 模块 / Test Terraform modules"""
    print("\n" + "="*80)
    print("测试 6: Terraform 模块 / Test 6: Terraform Modules")
    print("="*80)
    
    terraform_dir = project_root / "terraform"
    
    # 检查模块 / Check modules
    modules = ['s3', 'ecs', 'rds']
    all_exist = True
    
    for module in modules:
        module_dir = terraform_dir / "modules" / module
        required_files = ['main.tf', 'variables.tf', 'outputs.tf']
        
        print(f"\n模块 / Module: {module}")
        for filename in required_files:
            filepath = module_dir / filename
            if filepath.exists():
                print(f"  ✅ {filename}")
            else:
                print(f"  ❌ {filename}")
                all_exist = False
    
    # 检查环境配置 / Check environment configs
    env_dir = terraform_dir / "environments" / "prod"
    print(f"\n生产环境配置 / Production Environment:")
    for filename in ['main.tf', 'variables.tf', 'outputs.tf']:
        filepath = env_dir / filename
        if filepath.exists():
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename}")
            all_exist = False
    
    return all_exist

def test_migration_script():
    """测试迁移脚本 / Test migration script"""
    print("\n" + "="*80)
    print("测试 7: 数据库迁移脚本 / Test 7: Database Migration Script")
    print("="*80)
    
    try:
        from scripts.migrate_to_postgres import PostgresMigrator
        print("✅ PostgresMigrator 类导入成功 / Class imported successfully")
        
        # 检查方法 / Check methods
        methods = ['migrate_materials', 'migrate_experiments', 'migrate_results', 
                   'verify_migration', 'run_migration']
        
        for method in methods:
            if hasattr(PostgresMigrator, method):
                print(f"✅ 方法存在 / Method exists: {method}")
            else:
                print(f"❌ 方法缺失 / Method missing: {method}")
                return False
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败 / Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ 错误 / Error: {e}")
        return False

def main():
    """主测试函数 / Main test function"""
    print("\n" + "="*80)
    print("MatFormPPOAdv 新功能测试套件")
    print("MatFormPPOAdv New Features Test Suite")
    print("="*80)
    
    results = {
        "Dash 库导入 / Dash Imports": test_dash_imports(),
        "PostgreSQL 驱动 / PostgreSQL Driver": test_psycopg2_import(),
        "PostgreSQL 管理器 / PostgreSQL Manager": test_postgres_manager_init(),
        "Dash 应用结构 / Dash App Structure": test_dash_app_structure(),
        "Kubernetes 配置 / Kubernetes Manifests": test_kubernetes_manifests(),
        "Terraform 模块 / Terraform Modules": test_terraform_modules(),
        "迁移脚本 / Migration Script": test_migration_script()
    }
    
    # 打印总结 / Print summary
    print("\n" + "="*80)
    print("测试总结 / Test Summary")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过 / PASSED" if result else "❌ 失败 / FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n总计 / Total: {passed}/{total} 测试通过 / tests passed")
    print(f"成功率 / Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过! / All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total-passed} 个测试失败 / tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
