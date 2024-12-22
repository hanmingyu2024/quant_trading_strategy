import os
import shutil
from pathlib import Path

# 定义项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# 定义需要跳过的文件名称（无需移动或创建的文件）
SKIP_FILES = [
    # 在此添加需要跳过的文件名称，如 'README.md'
]

# 定义目标目录结构
DIRECTORIES = [
    ".github/workflows",
    "backend/alembic/versions",
    "backend/app/api/v1",
    "backend/app/core",
    "backend/app/exceptions",
    "backend/app/middlewares",
    "backend/app/migrations/versions",
    "backend/app/models",
    "backend/app/routes",
    "backend/app/schemas",
    "backend/app/services",
    "backend/app/static/css",
    "backend/app/static/images",
    "backend/app/static/js",
    "backend/app/strategies",
    "backend/app/templates/email",
    "backend/app/utils",
    "backend/database/recovery",
    "backend/monitoring/grafana",
    "backend/monitoring/prometheus",
    "backend/monitoring/ELK",
    "backend/scripts",
    "backend/tests",
    "backend/security",
    "backups/daily",
    "backups/weekly",
    "config/i18n",
    "data/samples",
    "docs/api",
    "docs/architecture",
    "docs/deployment",
    "frontend/public",
    "frontend/src/__tests__",
    "frontend/src/assets",
    "frontend/src/components/admin",
    "frontend/src/hooks",
    "frontend/src/pages",
    "frontend/src/services",
    "frontend/src/store/actions",
    "frontend/src/store/reducers",
    "frontend/src/store",
    "frontend/src/styles/admin",
    "frontend/src/utils",
    "frontend/src/i18n",
    "logs/app",
    "logs/db",
    "logs/maintenance",
    "logs/trade",
    "logs/setup",
    "tests/integration",
    "tools/project",
    "tools/security",
    "backend/tests/logs",
    "backend/tests/reports"
]

# 定义目标文件结构
FILES = [
    # .github/workflows/
    ".github/workflows/ci.yml",
    ".github/workflows/deploy.yml",
    ".github/workflows/quality.yml",
    ".github/workflows/security_audit.yml",

    # backend/alembic/
    "backend/alembic/README.md",
    "backend/alembic/script.py.mako",
    "backend/alembic/env.py",

    # backend/app/api/v1/
    "backend/app/api/v1/__init__.py",
    "backend/app/api/v1/admin.py",
    "backend/app/api/v1/auth.py",
    "backend/app/api/v1/password_reset.py",
    "backend/app/api/v1/users.py",

    # backend/app/api/
    "backend/app/api/__init__.py",
    "backend/app/api/deps.py",

    # backend/app/core/
    "backend/app/core/__init__.py",
    "backend/app/core/config.py",
    "backend/app/core/config_backup.py",
    "backend/app/core/settings.py",

    # backend/app/exceptions/
    "backend/app/exceptions/__init__.py",
    "backend/app/exceptions/auth_exception.py",
    "backend/app/exceptions/base_exception.py",
    "backend/app/exceptions/business_exception.py",
    "backend/app/exceptions/validation_exception.py",

    # backend/app/middlewares/
    "backend/app/middlewares/__init__.py",
    "backend/app/middlewares/auth_middleware.py",
    "backend/app/middlewares/error_handler.py",
    "backend/app/middlewares/error_handler_middleware.py",
    "backend/app/middlewares/exception_handler_middleware.py",
    "backend/app/middlewares/logging_middleware.py",
    "backend/app/middlewares/rate_limit_middleware.py",
    "backend/app/middlewares/security.py",

    # backend/app/migrations/versions/
    "backend/app/migrations/versions/__init__.py",
    "backend/app/migrations/versions/create_password_history.py",

    # backend/app/models/
    "backend/app/models/__init__.py",
    "backend/app/models/account.py",
    "backend/app/models/base.py",
    "backend/app/models/base_backup.py",
    "backend/app/models/password_history.py",
    "backend/app/models/password_reset.py",
    "backend/app/models/strategy.py",
    "backend/app/models/trade.py",
    "backend/app/models/user.py",

    # backend/app/routes/
    "backend/app/routes/__init__.py",
    "backend/app/routes/trades.py",

    # backend/app/schemas/
    "backend/app/schemas/__init__.py",
    "backend/app/schemas/trade.py",
    "backend/app/schemas/user.py",

    # backend/app/services/
    "backend/app/services/__init__.py",
    "backend/app/services/auth_service.py",
    "backend/app/services/password_reset_service.py",
    "backend/app/services/rate_limiter.py",
    "backend/app/services/strategy_service.py",
    "backend/app/services/trade_service.py",
    "backend/app/services/user_service.py",

    # backend/app/static/js/
    "backend/app/static/js/test.js",

    # backend/app/strategies/
    "backend/app/strategies/base_strategy.py",
    "backend/app/strategies/base_strategy_backup.py",
    "backend/app/strategies/ma_cross_strategy.py",

    # backend/app/templates/email/
    "backend/app/templates/email/password_reset.html",
    "backend/app/templates/email/password_reset_success.html",

    # backend/app/templates/
    "backend/app/templates/reset_password.html",

    # backend/app/utils/
    "backend/app/utils/__init__.py",
    "backend/app/utils/alert_manager.py",
    "backend/app/utils/alert_rules.py",
    "backend/app/utils/alert_types.py",
    "backend/app/utils/database.py",
    "backend/app/utils/database_backup.py",
    "backend/app/utils/error_handler.py",
    "backend/app/utils/init_db.py",
    "backend/app/utils/log_monitor.py",
    "backend/app/utils/logger.py",
    "backend/app/utils/logger_backup.py",
    "backend/app/utils/mail_service.py",
    "backend/app/utils/monitoring.py",
    "backend/app/utils/oauth2.py",
    "backend/app/utils/password.py",
    "backend/app/utils/password_expiry.py",
    "backend/app/utils/password_validator.py",
    "backend/app/utils/queue_manager.py",
    "backend/app/utils/rate_limiter.py",
    "backend/app/utils/response.py",
    "backend/app/utils/security.py",
    "backend/app/utils/template_manager.py",
    "backend/app/utils/token_validator.py",

    # backend/app/
    "backend/app/__init__.py",
    "backend/app/exceptions.py",
    "backend/app/main.py",

    # backend/database/
    "backend/database/__init__.py",
    "backend/database/backup_database.py",
    "backend/database/clean_db.py",
    "backend/database/maintain_database.py",
    "backend/database/optimize_database.py",
    "backend/database/reset_alembic.py",

    # backend/database/recovery/
    "backend/database/recovery/recovery_script.py",
    "backend/database/recovery/recovery_readme.md",

    # backend/monitoring/grafana/
    "backend/monitoring/grafana/grafana.yml",

    # backend/monitoring/prometheus/
    "backend/monitoring/prometheus/prometheus.yml",

    # backend/monitoring/ELK/
    "backend/monitoring/ELK/elasticsearch.yml",
    "backend/monitoring/ELK/logstash.conf",
    "backend/monitoring/ELK/kibana.yml",

    # backend/scripts/
    "backend/scripts/__init__.py",
    "backend/scripts/schedule_maintenance.bat",
    "backend/scripts/security_audit.sh",
    "backend/scripts/performance_test.sh",

    # backend/tests/
    "backend/tests/__init__.py",
    "backend/tests/analyze_db.py",
    "backend/tests/check_structure.py",
    "backend/tests/conftest.py",
    "backend/tests/conftest_backup.py",
    "backend/tests/quick_db_test.py",
    "backend/tests/run_check.py",
    "backend/tests/run_coverage.py",
    "backend/tests/setup_project.py",
    "backend/tests/test_admin.py",
    "backend/tests/test_advanced_operations.py",
    "backend/tests/test_api.py",
    "backend/tests/test_auth.py",
    "backend/tests/test_base.py",
    "backend/tests/test_base_backup.py",
    "backend/tests/test_components.py",
    "backend/tests/test_config.py",
    "backend/tests/test_config_backup.py",
    "backend/tests/test_data_operations.py",
    "backend/tests/test_db.py",
    "backend/tests/test_db_connection.py",
    "backend/tests/test_db_tables.py",
    "backend/tests/test_email.py",
    "backend/tests/test_env.py",
    "backend/tests/test_health.py",
    "backend/tests/test_imports.py",
    "backend/tests/test_log_monitor.py",
    "backend/tests/test_log_monitor_advanced.py",
    "backend/tests/test_logger.py",
    "backend/tests/test_models.py",
    "backend/tests/test_password_expiry.py",
    "backend/tests/test_password_reset.py",
    "backend/tests/test_password_security.py",
    "backend/tests/test_performance.py",
    "backend/tests/test_strategy.py",
    "backend/tests/test_trades.py",
    "backend/tests/test_users.py",
    "backend/tests/verify_data.py",

    # backend/.flake8
    "backend/.flake8",

    # backend/
    "backend/__init__.py",
    "backend/alembic.ini",
    "backend/Dockerfile",
    "backend/pytest.ini",
    "backend/requirements-dev.txt",
    "backend/requirements.txt",

    # backend/security/
    "backend/security/secrets.example.env",
    "backend/security/README.md",

    # backups/daily/
    # backups/weekly/
    # data/samples/
    # data/trading.db

    # docs/api/
    "docs/api/endpoints.md",
    "docs/api/swagger.json",

    # docs/architecture/
    "docs/architecture/decisions.md",
    "docs/architecture/overview.md",

    # docs/deployment/
    "docs/deployment/docker.md",
    "docs/deployment/kubernetes.md",

    # docs/
    "docs/api_documentation.md",
    "docs/contribution.md",
    "docs/deployment.md",
    "docs/project_stats.json",
    "docs/project_structure.md",
    "docs/user_guide.md",
    "docs/security.md",

    # frontend/public/
    "frontend/public/favicon.ico",
    "frontend/public/index.html",
    "frontend/public/robots.txt",

    # frontend/src/__tests__/
    "frontend/src/__tests__/App.test.jsx",

    # frontend/src/assets/
    "frontend/src/assets/logo.png",

    # frontend/src/components/admin/
    "frontend/src/components/admin/AlertConfig.tsx",
    "frontend/src/components/admin/EmailMonitor.tsx",

    # frontend/src/components/
    "frontend/src/components/Header.jsx",
    "frontend/src/components/PasswordReset.jsx",
    "frontend/src/components/PasswordStrengthIndicator.tsx",
    "frontend/src/components/TradeForm.jsx",
    "frontend/src/components/TradeList.jsx",

    # frontend/src/hooks/
    "frontend/src/hooks/useAuth.js",
    "frontend/src/hooks/useTrades.js",

    # frontend/src/pages/
    "frontend/src/pages/Dashboard.jsx",
    "frontend/src/pages/Login.jsx",
    "frontend/src/pages/Register.jsx",

    # frontend/src/services/
    "frontend/src/services/api.js",
    "frontend/src/services/auth.js",

    # frontend/src/store/actions/
    "frontend/src/store/actions/authActions.js",

    # frontend/src/store/reducers/
    "frontend/src/store/reducers/authReducer.js",

    # frontend/src/store/
    "frontend/src/store/index.js",

    # frontend/src/styles/admin/
    "frontend/src/styles/admin/EmailMonitor.scss",

    # frontend/src/styles/
    "frontend/src/styles/App.css",
    "frontend/src/styles/App.scss",
    "frontend/src/styles/PasswordReset.scss",
    "frontend/src/styles/PasswordStrengthIndicator.scss",
    "frontend/src/styles/variables.scss",
    "frontend/src/styles/i18n.scss",

    # frontend/src/utils/
    "frontend/src/utils/api.ts",
    "frontend/src/utils/error.ts",
    "frontend/src/utils/helpers.js",
    "frontend/src/utils/passwordValidation.ts",

    # frontend/src/i18n/
    "frontend/src/i18n/en.json",
    "frontend/src/i18n/zh.json",

    # frontend/
    "frontend/App.jsx",
    "frontend/App.tsx",
    "frontend/index.js",

    # frontend/.env
    "frontend/.env",

    # frontend/.eslintrc.js
    "frontend/.eslintrc.js",

    # frontend/.prettierrc
    "frontend/.prettierrc",

    # frontend/Dockerfile
    "frontend/Dockerfile",

    # frontend/jest.config.js
    "frontend/jest.config.js",

    # frontend/nginx.conf
    "frontend/nginx.conf",

    # frontend/package-lock.json
    "frontend/package-lock.json",

    # frontend/package.json
    "frontend/package.json",

    # frontend/webpack.config.js
    "frontend/webpack.config.js",

    # logs/app/
    "logs/app/app.log",
    "logs/app/app_20241219.log",
    "logs/app/backup_20241218.log",
    "logs/app/backup_20241219.log",

    # logs/db/
    "logs/db/db_maintenance_20241218.log",
    "logs/db/db_maintenance_20241219.log",
    "logs/db/quant_trading.log",

    # logs/maintenance/
    "logs/maintenance/maintenance_report_20241218.txt",
    "logs/maintenance/maintenance_report_20241219.txt",

    # logs/trade/
    "logs/trade/quant_trading.log",

    # logs/setup/
    "logs/setup/setup.log",

    # modules/
    "modules/__init__.py",
    "modules/backtest.py",
    "modules/data_handler.py",
    "modules/database.py",
    "modules/logger.py",
    "modules/mt5_connector.py",
    "modules/performance.py",
    "modules/risk_manager.py",
    "modules/strategy.py",
    "modules/trade_executor.py",

    # monitoring/apm/
    "monitoring/apm/elastic_apm.yml",

    # monitoring/metrics/
    "monitoring/metrics/prometheus.yml",

    # monitoring/ELK/
    "monitoring/ELK/elasticsearch.yml",
    "monitoring/ELK/logstash.conf",
    "monitoring/ELK/kibana.yml",

    # reports/
    "reports/trade_report_20241217.csv",
    "reports/performance_report_20241217.pdf",

    # tests/
    "tests/conftest.py",
    "tests/integration/test_integration_auth.py",
    "tests/integration/test_integration_trades.py",

    # tools/project/
    "tools/project/__init__.py",
    "tools/project/model_downloader.py",
    "tools/project/project_builder.py",
    "tools/project/structure.py",
    "tools/project/structure_scanner.py",

    # tools/security/
    "tools/security/vulnerability_scanner.py",
    "tools/security/README.md",

    # tools/
    "tools/__init__.py",

    # 根目录文件
    ".coverage",
    ".env",
    ".env_backup",
    ".gitignore",
    ".pre-commit-config.yaml",
    "alembic.ini",
    "api.py",
    "backtest_results.json",
    "docker-compose.dev.yml",
    "docker-compose.prod.yml",
    "docker-compose.yml",
    "docker-compose_backup.yml",
    "quant_trading.db",
    "README.md",
    "requirements.txt",
    "requirements_backup.txt",
    "setup.cfg",
    "setup.py",
    "tools.ps1",
    "config/logging_config.yaml",
    "config/monitoring.yaml",
    "config/trading_params.yaml",
    "backend/tests/logs/setup.log"
]

# 定义需要移动的文件映射（文件名: 新路径）
# 如果文件存在多个相同名称的位置，可能需要更精确的匹配
FILE_MOVES = {
    # "old_path/filename.ext": "new_path/filename.ext",
    # 示例:
    # "backend/app/old_file.py": "backend/app/new_file.py",
}

def create_directories():
    for dir_path in DIRECTORIES:
        full_path = PROJECT_ROOT / dir_path
        if not full_path.exists():
            print(f"Creating directory: {full_path}")
            full_path.mkdir(parents=True, exist_ok=True)
        else:
            print(f"Directory already exists: {full_path}")

def create_files():
    for file_path in FILES:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"File already exists: {full_path}")
            continue
            
        # 确保父目录存在
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 创建文件
        print(f"Creating empty file: {full_path}")
        full_path.touch()

def move_files():
    for src, dest in FILE_MOVES.items():
        src_path = PROJECT_ROOT / src
        dest_path = PROJECT_ROOT / dest
        if not src_path.exists():
            print(f"Source file does not exist, skipping: {src_path}")
            continue
        if dest_path.exists():
            print(f"Destination file already exists, skipping: {dest_path}")
            continue
        # Ensure destination directory exists
        dest_dir = dest_path.parent
        if not dest_dir.exists():
            print(f"Creating directory for destination: {dest_dir}")
            dest_dir.mkdir(parents=True, exist_ok=True)
        # Move the file
        print(f"Moving {src_path} to {dest_path}")
        shutil.move(str(src_path), str(dest_path))

def search_and_move_files():
    """
    搜索整个项目中需要移动的文件并移动到指定位置
    """
    for file_name, new_rel_path in FILE_MOVES.items():
        if file_name in SKIP_FILES:
            print(f"Skipping file: {file_name}")
            continue
        # Search for the file in the project
        found = False
        for dirpath, _, filenames in os.walk(PROJECT_ROOT):
            if file_name in filenames:
                old_path = Path(dirpath) / file_name
                new_path = PROJECT_ROOT / new_rel_path
                if new_path.exists():
                    print(f"Destination file already exists, skipping: {new_path}")
                    continue
                # Ensure the new directory exists
                new_path.parent.mkdir(parents=True, exist_ok=True)
                print(f"Moving {old_path} to {new_path}")
                shutil.move(str(old_path), str(new_path))
                found = True
                break
        if not found:
            print(f"File not found, will create empty file: {new_rel_path}")
            empty_file = PROJECT_ROOT / new_rel_path
            empty_file.touch()

def main():
    print("Starting directory and file restructuring...")
    create_directories()
    search_and_move_files()
    create_files()
    print("Restructuring completed.")

if __name__ == "__main__":
    main()
