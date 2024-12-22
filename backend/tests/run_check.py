from check_structure import setup_project
import sys
from pathlib import Path

def run_full_check():
    """运行完整检查"""
    print("\n=== 开始项目结构检查 ===")
    
    # 1. 检查Python路径
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
        print(f"添加项目根目录到Python路径: {project_root}")
    
    # 2. 运行结构检查
    setup_project()
    
    # 3. 验证配置
    try:
        from backend.app.config.config import Config
        from backend.app.core.base import BaseClass
        print("\n基础类导入成功!")
        
        from backend.tests.test_config import TestConfig
        from backend.tests.test_base import TestBase
        print("测试类导入成功!")
        
    except ImportError as e:
        print(f"\n导入错误: {e}")
        print("请检查文件内容是否正确!")
        return False
    
    # 4. 检查目录权限
    dirs_to_check = [
        project_root / 'tests' / 'logs',
        project_root / 'tests' / 'reports'
    ]
    
    for dir_path in dirs_to_check:
        try:
            # 测试写入权限
            test_file = dir_path / 'test.txt'
            test_file.write_text('test')
            test_file.unlink()  # 删除测试文件
            print(f"目录权限正常: {dir_path}")
        except PermissionError:
            print(f"警告: 无写入权限: {dir_path}")
            return False
    
    print("\n=== 项目结构检查完成 ===")
    return True

def show_project_structure():
    """显示项目结构"""
    project_root = Path(__file__).parent.parent
    
    def print_tree(path, prefix=""):
        """打印目录树"""
        if path.is_file():
            print(f"{prefix}└── {path.name}")
        else:
            print(f"{prefix}└── {path.name}/")
            prefix += "    "
            for child in sorted(path.iterdir()):
                if child.name not in ['__pycache__', '.git', '.pytest_cache']:
                    print_tree(child, prefix)
    
    print("\n=== 项目结构 ===")
    print_tree(project_root)

if __name__ == "__main__":
    if run_full_check():
        print("\n项目结构检查通过!")
        show_project_structure()
        
        print("\n下一步:")
        print("1. 检查生成的配置文件")
        print("2. 根据需要修改配置")
        print("3. 运行覆盖率测试")
    else:
        print("\n项目结构检查失败!")
        print("请解决上述问题后重试。") 