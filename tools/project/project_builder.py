import os
import shutil
from pathlib import Path

class ProjectBuilder:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        
    def create_directory(self, path):
        """创建目录，如果不存在的话"""
        dir_path = self.root_dir / path
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"创建目录: {path}")
        
    def create_file(self, path, content=""):
        """创建文件，如果不存在的话"""
        file_path = self.root_dir / path
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"创建文件: {path}")
            
    def get_all_paths(self):
        """获取所有应该存在的路径"""
        paths = set()
        
        # 添加所有目录
        for dir_path in self.backend_dirs + self.frontend_dirs + self.other_dirs:
            paths.add(str(Path(dir_path)))
        
        # 添加所有文件
        for file_path in (self.backend_files + self.frontend_files + 
                         self.config_files + self.doc_files + self.other_files):
            paths.add(str(Path(file_path)))
        
        return paths

    def clean_extra_files(self):
        """清理多余的文件和目录"""
        # 需要删除的具体文件和目录
        to_remove = [
            "backend/migrations",
            "frontend/src/store/actions/index.js",
            "frontend/src/store/reducers/index.js",
            "frontend/.env.example",
            "tests",
            "main.py"
        ]
        
        for path in to_remove:
            full_path = self.root_dir / path
            if full_path.exists():
                if full_path.is_file():
                    full_path.unlink()
                    print(f"删除多余文件: {path}")
                else:
                    shutil.rmtree(full_path)
                    print(f"删除多余目录: {path}")

    def build_structure(self):
        """构建项目结构"""
        # 后端结构
        self.backend_dirs = [
            "backend/alembic/versions",
            "backend/app/models",
            "backend/app/routes",
            "backend/app/schemas",
            "backend/app/services",
            "backend/app/utils",
            "backend/monitoring",
            "backend/tests"
        ]
        
        # 前端结构
        self.frontend_dirs = [
            "frontend/public",
            "frontend/src/assets",
            "frontend/src/components",
            "frontend/src/hooks",
            "frontend/src/pages",
            "frontend/src/services",
            "frontend/src/store/actions",
            "frontend/src/store/reducers",
            "frontend/src/styles",
            "frontend/src/utils",
            "frontend/src/__tests__"
        ]
        
        # 其他目录
        self.other_dirs = [
            ".github/workflows",
            "config",
            "data/samples",
            "docs/api",
            "docs/architecture",
            "docs/deployment",
            "logs",
            "modules",
            "reports",
            "tools/project"
        ]
        
        # 创建所有目录
        for dir_path in self.backend_dirs + self.frontend_dirs + self.other_dirs:
            self.create_directory(dir_path)
            
        # 后端文件
        self.backend_files = [
            # 应用核心文件
            "backend/app/__init__.py",
            "backend/app/main.py",
            # 数据模型
            "backend/app/models/__init__.py",
            "backend/app/models/trade.py",
            "backend/app/models/user.py",
            # 路由
            "backend/app/routes/__init__.py",
            "backend/app/routes/auth.py",
            "backend/app/routes/trades.py",
            "backend/app/routes/users.py",
            # 数据模式
            "backend/app/schemas/__init__.py",
            "backend/app/schemas/trade.py",
            "backend/app/schemas/user.py",
            # 服务
            "backend/app/services/__init__.py",
            "backend/app/services/auth_service.py",
            "backend/app/services/trade_service.py",
            "backend/app/services/user_service.py",
            # 工具
            "backend/app/utils/__init__.py",
            "backend/app/utils/database.py",
            "backend/app/utils/security.py",
            # 测试
            "backend/tests/__init__.py",
            "backend/tests/test_auth.py",
            "backend/tests/test_trades.py",
            "backend/tests/test_users.py",
            # 监控
            "backend/monitoring/grafana.yml",
            "backend/monitoring/prometheus.yml",
            # 配置文件
            "backend/.env.example",
            "backend/.flake8",
            "backend/alembic.ini",
            "backend/Dockerfile",
            "backend/pytest.ini",
            "backend/requirements.txt"
        ]
        
        # 前端文件
        self.frontend_files = [
            # 公共文件
            "frontend/public/favicon.ico",
            "frontend/public/index.html",
            "frontend/public/robots.txt",
            # 核心文件
            "frontend/src/App.jsx",
            "frontend/src/index.js",
            # 组件
            "frontend/src/components/Header.jsx",
            "frontend/src/components/TradeForm.jsx",
            "frontend/src/components/TradeList.jsx",
            # Hooks
            "frontend/src/hooks/useAuth.js",
            # 页面
            "frontend/src/pages/Dashboard.jsx",
            "frontend/src/pages/Login.jsx",
            "frontend/src/pages/Register.jsx",
            # 服务
            "frontend/src/services/api.js",
            "frontend/src/services/auth.js",
            # 状态管理
            "frontend/src/store/actions/authActions.js",
            "frontend/src/store/reducers/authReducer.js",
            "frontend/src/store/index.js",
            # 样式
            "frontend/src/styles/App.css",
            "frontend/src/styles/variables.scss",
            # 工具
            "frontend/src/utils/helpers.js",
            # 测试
            "frontend/src/__tests__/App.test.jsx",
            # 资源
            "frontend/src/assets/logo.png",
            # 配置文件
            "frontend/.eslintrc.js",
            "frontend/.prettierrc",
            "frontend/Dockerfile",
            "frontend/jest.config.js",
            "frontend/package.json"
        ]
        
        # 配置文件
        self.config_files = [
            "config/config.py",
            "config/logging_config.yaml",
            "config/monitoring.yaml",
            "config/trading_params.yaml"
        ]
        
        # 文档文件
        self.doc_files = [
            "docs/api/endpoints.md",
            "docs/api/swagger.json",
            "docs/architecture/decisions.md",
            "docs/architecture/overview.md",
            "docs/deployment/docker.md",
            "docs/deployment/kubernetes.md",
            "docs/api_documentation.md",
            "docs/contribution.md",
            "docs/deployment.md",
            "docs/project_stats.json",
            "docs/project_structure.md",
            "docs/user_guide.md"
        ]
        
        # 其他文件
        self.other_files = [
            ".env",
            ".env.example",
            ".gitignore",
            "backtest_results.json",
            "docker-compose.dev.yml",
            "docker-compose.prod.yml",
            "docker-compose.yml",
            "Makefile",
            "README.md",
            "requirements.txt",
            "setup.py"
        ]
        
        # 创建所有文件
        for file_path in (self.backend_files + self.frontend_files + 
                         self.config_files + self.doc_files + self.other_files):
            self.create_file(file_path)
            
        # 清理多余的文件
        self.clean_extra_files()

def main():
    root_dir = Path(__file__).parent.parent.parent
    builder = ProjectBuilder(root_dir)
    builder.build_structure()
    print("项目结构更新完成！")

if __name__ == "__main__":
    main()