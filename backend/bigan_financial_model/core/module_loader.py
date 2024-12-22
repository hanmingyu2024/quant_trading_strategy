"""
模块加载器

提供动态加载和管理模块的功能
作者: BiGan团队
日期: 2024-01
"""

import importlib
import inspect
from typing import Dict, Any

class ModuleLoader:
    def __init__(self):
        self.modules: Dict[str, Any] = {}
    
    def load_module(self, module_path: str, class_name: str = None):
        """动态加载模块"""
        try:
            module = importlib.import_module(module_path)
            if class_name:
                return getattr(module, class_name)
            return module
        except Exception as e:
            raise ImportError(f"无法加载模块 {module_path}: {str(e)}")
    
    def register_module(self, name: str, module_path: str, class_name: str = None):
        """注册模块"""
        module = self.load_module(module_path, class_name)
        self.modules[name] = module
        return module
    
    def get_module(self, name: str):
        """获取已注册的模块"""
        return self.modules.get(name)
