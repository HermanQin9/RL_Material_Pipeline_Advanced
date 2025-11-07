"""
Docker Container Test Script

"""

import sys
import os

def test_imports():
    """"""
    print("=" * 60)
    print(" Testing Package Imports")
    print("=" * 60)
    
    packages = [
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('torch', 'PyTorch'),
        ('sklearn', 'scikit-learn'),
        ('xgboost', 'XGBoost'),
        ('catboost', 'CatBoost'),
        ('mp_api', 'Materials Project API'),
    ]
    
    for module, name in packages:
        try:
            imported = __import__(module)
            version = getattr(imported, '__version__', 'N/A')
            print(f" {name:25s} {version}")
        except ImportError as e:
            print(f" {name:25s} FAILED: {e}")
            return False
    
    return True

def test_project_structure():
    """"""
    print("\n" + "=" * 60)
    print(" Testing Project Structure")
    print("=" * 60)
    
    required_paths = [
        'config.py',
        'nodes.py',
        'pipeline.py',
        'env/pipeline_env.py',
        'methods/data_methods.py',
        'methods/model_methods.py',
        'ppo/trainer.py',
        'ppo/policy.py',
    ]
    
    all_exist = True
    for path in required_paths:
        exists = os.path.exists(path)
        status = "" if exists else ""
        print(f"{status} {path}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_python_version():
    """ Python """
    print("\n" + "=" * 60)
    print(" Python Environment")
    print("=" * 60)
    
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    print(f"Python Path: {sys.executable}")
    
    return version.major == 3 and version.minor >= 11

def main():
    """"""
    print("\n Docker Container Environment Test")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Package Imports", test_imports),
        ("Project Structure", test_project_structure),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n {name} failed with exception: {e}")
            results.append((name, False))
    
    # 
    print("\n" + "=" * 60)
    print(" Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = " PASS" if result else " FAIL"
        print(f"{status:8s} {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print(" All tests passed! Container is ready.")
        return 0
    else:
        print(" Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
