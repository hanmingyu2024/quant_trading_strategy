from setuptools import setup, find_packages

setup(
    name="quant_trading_strategy",
    version="0.1.0",
    description="A quantitative trading strategy system",
    author="Your Name",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "pydantic",
        "pydantic-settings",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "pymysql",
        "alembic",
        "pytest",
        "email-validator",
    ],
    extras_require={
        "dev": [
            "pytest",
            "flake8",
            "black",
            "isort",
            "mypy",
        ],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "quant-trading=backend.app.main:main",
        ],
    },
    package_data={
        "": ["*.yaml", "*.json", "*.md"],
    },
)
