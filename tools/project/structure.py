"""
项目结构生成模块

用于生成项目的文件结构树,并输出到markdown文件中。
支持自定义忽略模式,可以排除不需要显示的文件和目录。
"""

from pathlib import Path
import os
from typing import Dict, Set
from datetime import datetime
import json

class ProjectStructureGenerator:
    """项目结构生成器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "docs"
        self.structure_file = self.output_dir / "project_structure.md"
        
        # 默认忽略模式
        self.ignore_patterns = {
            '__pycache__', 
            '.git', 
            '.pytest_cache', 
            '*.pyc', 
            '.venv',
            'venv',
            'dist',
            'build',
            '*.egg-info',
            '.idea',
            '.vscode',
            'node_modules',
            '.DS_Store',
            '.mypy_cache'  # 添加.mypy_cache到忽略列表
        }
        
        # 统计信息
        self.file_types: Dict[str, int] = {}
        self.total_files = 0
        self.total_dirs = 0
        
    def _should_ignore(self, path: str) -> bool:
        """检查是否应该忽略该路径"""
        name = os.path.basename(path)
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif pattern == name:
                return True
        return False
    
    def _get_tree(self, dir_path: Path, prefix: str = "") -> str:
        """递归生成目录树"""
        if self._should_ignore(str(dir_path)):
            return ""
        
        output = []
        
        # 获取目录内容
        try:
            entries = list(dir_path.iterdir())
        except PermissionError:
            return ""
        
        # 分离目录和文件
        dirs = sorted([e for e in entries if e.is_dir()])
        files = sorted([e for e in entries if e.is_file()])
        
        # 处理所有项目
        entries = dirs + files
        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)
            
            if self._should_ignore(str(entry)):
                continue
                
            # 确定当前项的前缀
            current_prefix = "└── " if is_last else "├── "
            
            # 添加当前项
            if entry.is_dir():
                self.total_dirs += 1
                output.append(f"{prefix}{current_prefix}{entry.name}/")
                # 递归处理子目录，注意缩进
                next_prefix = prefix + ("    " if is_last else "│   ")
                output.append(self._get_tree(entry, next_prefix))
            else:
                self.total_files += 1
                # 统计文件类型
                ext = entry.suffix or '(no extension)'
                self.file_types[ext] = self.file_types.get(ext, 0) + 1
                output.append(f"{prefix}{current_prefix}{entry.name}")
        
        return "\n".join(filter(None, output))
    
    def _save_stats(self):
        """保存详细统计信息到JSON文件"""
        # 计算正确的文件类型统计
        file_extensions = {
            "source_files": self.file_types.get(".py", 0),
            "documentation": (self.file_types.get(".md", 0) + 
                            self.file_types.get(".txt", 0)),
            "configuration": (self.file_types.get(".json", 0) + 
                            self.file_types.get(".yaml", 0) +
                            self.file_types.get(".toml", 0) +
                            self.file_types.get(".ini", 0)),
            "other": sum(count for ext, count in self.file_types.items()
                        if ext not in [".py", ".md", ".txt", ".json", 
                                     ".yaml", ".toml", ".ini"])
        }
        
        stats = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "project_name": self.project_root.name,
                "total_dirs": self.total_dirs,
                "total_files": self.total_files
            },
            "file_types": {
                ext: {
                    "count": count,
                    "percentage": round((count / self.total_files) * 100, 1)
                }
                for ext, count in self.file_types.items()
            },
            "directory_structure": {
                "root_dir": str(self.project_root),
                "directories": self.total_dirs,
                "files": self.total_files
            },
            "file_extensions": file_extensions
        }
        
        # 保存到JSON文件
        stats_file = self.output_dir / "project_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"统计信息已保存到: {stats_file}")
    
    def generate(self):
        """生成项目结构文档"""
        print("正在生成项目结构文档...")
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.structure_file, 'w', encoding='utf-8') as f:
            # 写入头部
            f.write(f"# 项目文件结构\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 生成并写入目录树
            f.write("```\n")
            f.write(f"{self.project_root.name}/\n")
            f.write(self._get_tree(self.project_root))
            f.write("\n```\n\n")
            
            # 写入统计信息
            f.write(f"## 统计信息\n\n")
            f.write(f"- 总目录数: {self.total_dirs}\n")
            f.write(f"- 总文件数: {self.total_files}\n\n")
            
            # 写入文件类型统计
            f.write("### 文件类型分布\n\n")
            for ext, count in sorted(self.file_types.items(), 
                                   key=lambda x: (-x[1], x[0])):
                percentage = (count / self.total_files) * 100
                f.write(f"- {ext}: {count} ({percentage:.1f}%)\n")
            
            # 写入说明
            f.write("\n## 说明\n\n")
            f.write("- `├──` 表示目录或文件的分支\n")
            f.write("- `└──` 表示目录或文件的末端\n")
            f.write("- `/` 结尾表示目录\n")
            f.write("- 已忽略以下内容：\n")
            for pattern in sorted(self.ignore_patterns):
                f.write(f"  - `{pattern}`\n")
        
        print(f"文档已生成到: {self.structure_file}")
        self._save_stats()

def main():
    # 获取正确的项目根目录路径
    project_root = "I:/quant_trading_strategy"
    docs_path = os.path.join(project_root, "docs")

    # 确保 docs 目录存在
    if not os.path.exists(docs_path):
        os.makedirs(docs_path)

    print("项目根目录:", project_root)
    print("正在生成项目结构文档...")
    print(f"文档已生成到: {os.path.join(docs_path, 'project_structure.md')}")
    print(f"统计信息已保存到: {os.path.join(docs_path, 'project_stats.json')}")

    # 创建生成器
    generator = ProjectStructureGenerator(Path(project_root))
    
    # 更新忽略模式
    generator.ignore_patterns.update({
        'cache',
        '__pycache__',
        '.pytest_cache',
        '.idea',
        '.vscode',
        'node_modules',
        '.DS_Store',
        'dist',
        'build',
        '*.egg-info',
        '*.pyc',
        '.mypy_cache'  # 添加.mypy_cache到忽略列表
    })
    
    # 生成结构文档
    generator.generate()

if __name__ == "__main__":
    main() 