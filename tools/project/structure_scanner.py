"""
项目结构扫描器
"""
from pathlib import Path
from typing import Dict, List, Optional
import os

class ProjectScanner:
    """项目结构扫描器"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        
    def scan(self) -> Dict:
        """扫描项目结构"""
        return {
            "packages": self._find_packages(),
            "data_files": self._find_data_files(),
        }
        
    def _find_packages(self) -> List[str]:
        """查找所有Python包"""
        packages = []
        for path in self.root_path.rglob("__init__.py"):
            if "tests" not in str(path):
                package = str(path.parent.relative_to(self.root_path))
                if package != ".":
                    packages.append(package)
        return packages
        
    def _find_data_files(self) -> List[str]:
        """查找数据文件"""
        data_files = []
        data_extensions = {".json", ".yaml", ".yml", ".csv", ".txt"}
        for ext in data_extensions:
            for path in self.root_path.rglob(f"*{ext}"):
                if "tests" not in str(path):
                    data_files.append(str(path.relative_to(self.root_path)))
        return data_files 

def scan_project_structure(root_dir="."):
    print(f"开始扫描项目结构，根目录: {root_dir}")
    
    for root, dirs, files in os.walk(root_dir):
        level = root.replace(root_dir, '').count(os.sep)
        indent = '  ' * level
        print(f"{indent}{os.path.basename(root)}/")
        for file in files:
            print(f"{indent}  {file}")

if __name__ == "__main__":
    project_root = "I:/quant_trading_strategy"
    scan_project_structure(project_root)