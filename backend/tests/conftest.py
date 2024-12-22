"""
测试配置文件

该文件包含测试所需的配置和fixture:
- 邮件发送模拟
- 数据库连接
- 认证令牌

主要功能:
    - 提供测试所需的各种fixture
    - 模拟外部依赖
    - 配置测试环境
"""

import pytest
from unittest.mock import patch
from backend.app.utils.email import EmailManager

@pytest.fixture(autouse=True)
def mock_email_sending():
    """自动模拟所有邮件发送"""
    with patch.object(EmailManager, 'send_email', return_value=None) as mock:
        yield mock 