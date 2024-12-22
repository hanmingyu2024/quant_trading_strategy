# 项目文件结构

生成时间: 2024-12-19 17:21:45

```
quant_trading_strategy/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── deploy.yml
│       └── quality.yml
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   │   ├── 1432ffd6eb86_add_trades_table.py
│   │   │   └── 628bad2506eb_initial_migration.py
│   │   ├── env.py
│   │   ├── README
│   │   └── script.py.mako
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── admin.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── password_reset.py
│   │   │   │   └── users.py
│   │   │   ├── __init__.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── config_backup.py
│   │   ├── exceptions/
│   │   │   ├── __init__.py
│   │   │   ├── auth_exception.py
│   │   │   ├── base_exception.py
│   │   │   ├── business_exception.py
│   │   │   └── validation_exception.py
│   │   ├── middlewares/
│   │   │   ├── __init__.py
│   │   │   ├── auth_middleware.py
│   │   │   ├── error_handler.py
│   │   │   ├── error_handler_middleware.py
│   │   │   ├── exception_handler_middleware.py
│   │   │   ├── logging_middleware.py
│   │   │   ├── rate_limit_middleware.py
│   │   │   └── security.py
│   │   ├── migrations/
│   │   │   ├── versions/
│   │   │   │   ├── __init__.py
│   │   │   │   └── create_password_history.py
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── account.py
│   │   │   ├── base.py
│   │   │   ├── base_backup.py
│   │   │   ├── password_history.py
│   │   │   ├── password_reset.py
│   │   │   ├── strategy.py
│   │   │   ├── trade.py
│   │   │   └── user.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── trades.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── trade.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── password_reset_service.py
│   │   │   ├── rate_limiter.py
│   │   │   ├── strategy_service.py
│   │   │   ├── trade_service.py
│   │   │   └── user_service.py
│   │   ├── static/
│   │   │   ├── css/
│   │   │   ├── images/
│   │   │   ├── js/
│   │   │   │   └── test.js
│   │   │   └── favicon.ico
│   │   ├── strategies/
│   │   │   ├── base_strategy.py
│   │   │   ├── base_strategy_backup.py
│   │   │   └── ma_cross_strategy.py
│   │   ├── templates/
│   │   │   ├── email/
│   │   │   │   ├── password_reset.html
│   │   │   │   └── password_reset_success.html
│   │   │   └── reset_password.html
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── alert_manager.py
│   │   │   ├── alert_rules.py
│   │   │   ├── alert_types.py
│   │   │   ├── database.py
│   │   │   ├── database_backup.py
│   │   │   ├── error_handler.py
│   │   │   ├── init_db.py
│   │   │   ├── log_monitor.py
│   │   │   ├── logger.py
│   │   │   ├── logger_backup.py
│   │   │   ├── mail_service.py
│   │   │   ├── monitoring.py
│   │   │   ├── oauth2.py
│   │   │   ├── password.py
│   │   │   ├── password_expiry.py
│   │   │   ├── password_validator.py
│   │   │   ├── queue_manager.py
│   │   │   ├── rate_limiter.py
│   │   │   ├── response.py
│   │   │   ├── security.py
│   │   │   ├── template_manager.py
│   │   │   └── token_validator.py
│   │   ├── __init__.py
│   │   ├── exceptions.py
│   │   └── main.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── backup_database.py
│   │   ├── clean_db.py
│   │   ├── maintain_database.py
│   │   ├── optimize_database.py
│   │   └── reset_alembic.py
│   ├── monitoring/
│   │   ├── grafana.yml
│   │   └── prometheus.yml
│   ├── scripts/
│   │   ├── __init__.py
│   │   └── schedule_maintenance.bat
│   ├── tests/
│   │   ├── logs/
│   │   │   └── setup.log
│   │   ├── reports/
│   │   ├── __init__.py
│   │   ├── analyze_db.py
│   │   ├── check_structure.py
│   │   ├── conftest.py
│   │   ├── conftest_backup.py
│   │   ├── quick_db_test.py
│   │   ├── run_check.py
│   │   ├── run_coverage.py
│   │   ├── setup_project.py
│   │   ├── test_admin.py
│   │   ├── test_advanced_operations.py
│   │   ├── test_api.py
│   │   ├── test_auth.py
│   │   ├── test_base.py
│   │   ├── test_base_backup.py
│   │   ├── test_components.py
│   │   ├── test_config.py
│   │   ├── test_config_backup.py
│   │   ├── test_data_operations.py
│   │   ├── test_db.py
│   │   ├── test_db_connection.py
│   │   ├── test_db_tables.py
│   │   ├── test_email.py
│   │   ├── test_env.py
│   │   ├── test_health.py
│   │   ├── test_imports.py
│   │   ├── test_log_monitor.py
│   │   ├── test_log_monitor_advanced.py
│   │   ├── test_logger.py
│   │   ├── test_models.py
│   │   ├── test_password_expiry.py
│   │   ├── test_password_reset.py
│   │   ├── test_password_security.py
│   │   ├── test_performance.py
│   │   ├── test_strategy.py
│   │   ├── test_trades.py
│   │   ├── test_users.py
│   │   └── verify_data.py
│   ├── .flake8
│   ├── __init__.py
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── pytest.ini
│   ├── requirements-dev.txt
│   └── requirements.txt
├── backups/
│   ├── daily/
│   └── weekly/
├── config/
│   ├── config.py
│   ├── config_backup.py
│   ├── logging_config.yaml
│   ├── monitoring.yaml
│   └── trading_params.yaml
├── data/
│   ├── samples/
│   └── trading.db
├── docs/
│   ├── api/
│   │   ├── endpoints.md
│   │   └── swagger.json
│   ├── architecture/
│   │   ├── decisions.md
│   │   └── overview.md
│   ├── deployment/
│   │   ├── docker.md
│   │   └── kubernetes.md
│   ├── api_documentation.md
│   ├── contribution.md
│   ├── deployment.md
│   ├── project_stats.json
│   ├── project_structure.md
│   └── user_guide.md
├── frontend/
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   └── robots.txt
│   ├── src/
│   │   ├── __tests__/
│   │   │   └── App.test.jsx
│   │   ├── assets/
│   │   │   └── logo.png
│   │   ├── components/
│   │   │   ├── admin/
│   │   │   │   ├── AlertConfig.tsx
│   │   │   │   └── EmailMonitor.tsx
│   │   │   ├── Header.jsx
│   │   │   ├── PasswordReset.jsx
│   │   │   ├── PasswordStrengthIndicator.tsx
│   │   │   ├── TradeForm.jsx
│   │   │   └── TradeList.jsx
│   │   ├── hooks/
│   │   │   ├── useAuth.js
│   │   │   └── useTrades.js
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Login.jsx
│   │   │   └── Register.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── auth.js
│   │   ├── store/
│   │   │   ├── actions/
│   │   │   │   └── authActions.js
│   │   │   ├── reducers/
│   │   │   │   └── authReducer.js
│   │   │   └── index.js
│   │   ├── styles/
│   │   │   ├── admin/
│   │   │   │   └── EmailMonitor.scss
│   │   │   ├── App.css
│   │   │   ├── App.scss
│   │   │   ├── PasswordReset.scss
│   │   │   ├── PasswordStrengthIndicator.scss
│   │   │   └── variables.scss
│   │   ├── utils/
│   │   │   ├── api.ts
│   │   │   ├── error.ts
│   │   │   ├── helpers.js
│   │   │   └── passwordValidation.ts
│   │   ├── App.jsx
│   │   ├── App.tsx
│   │   └── index.js
│   ├── .env
│   ├── .eslintrc.js
│   ├── .prettierrc
│   ├── Dockerfile
│   ├── jest.config.js
│   ├── nginx.conf
│   ├── package-lock.json
│   └── package.json
├── logs/
│   ├── app.log
│   ├── app_20241219.log
│   ├── backup_20241218.log
│   ├── backup_20241219.log
│   ├── db_maintenance_20241218.log
│   ├── db_maintenance_20241219.log
│   ├── maintenance_report_20241218.txt
│   ├── maintenance_report_20241219.txt
│   ├── quant_trading.log
│   └── setup.log
├── modules/
│   ├── __init__.py
│   ├── backtest.py
│   ├── data_handler.py
│   ├── database.py
│   ├── logger.py
│   ├── mt5_connector.py
│   ├── performance.py
│   ├── risk_manager.py
│   ├── strategy.py
│   └── trade_executor.py
├── monitoring/
│   ├── apm/
│   │   └── elastic_apm.yml
│   └── metrics/
│       └── prometheus.yml
├── reports/
│   └── trade_report_20241217.csv
├── tests/
│   └── conftest.py
├── tools/
│   ├── project/
│   │   ├── __init__.py
│   │   ├── model_downloader.py
│   │   ├── project_builder.py
│   │   ├── structure.py
│   │   └── structure_scanner.py
│   └── __init__.py
├── .coverage
├── .env
├── .env_backup
├── .gitignore
├── .pre-commit-config.yaml
├── alembic.ini
├── api.py
├── backtest_results.json
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── docker-compose.yml
├── docker-compose_backup.yml
├── quant_trading.db
├── README.md
├── requirements.txt
├── requirements_backup.txt
├── setup.cfg
├── setup.py
└── tools.ps1
```

## 统计信息

- 总目录数: 66
- 总文件数: 255

### 文件类型分布

- .py: 146 (57.3%)
- .js: 12 (4.7%)
- .md: 11 (4.3%)
- .yml: 11 (4.3%)
- (no extension): 10 (3.9%)
- .jsx: 9 (3.5%)
- .log: 9 (3.5%)
- .txt: 7 (2.7%)
- .json: 5 (2.0%)
- .scss: 5 (2.0%)
- .html: 4 (1.6%)
- .tsx: 4 (1.6%)
- .yaml: 4 (1.6%)
- .ini: 3 (1.2%)
- .ts: 3 (1.2%)
- .db: 2 (0.8%)
- .ico: 2 (0.8%)
- .bat: 1 (0.4%)
- .cfg: 1 (0.4%)
- .conf: 1 (0.4%)
- .css: 1 (0.4%)
- .csv: 1 (0.4%)
- .mako: 1 (0.4%)
- .png: 1 (0.4%)
- .ps1: 1 (0.4%)

## 说明

- `├──` 表示目录或文件的分支
- `└──` 表示目录或文件的末端
- `/` 结尾表示目录
- 已忽略以下内容：
  - `*.egg-info`
  - `*.pyc`
  - `.DS_Store`
  - `.git`
  - `.idea`
  - `.mypy_cache`
  - `.pytest_cache`
  - `.venv`
  - `.vscode`
  - `__pycache__`
  - `build`
  - `cache`
  - `dist`
  - `node_modules`
  - `venv`
