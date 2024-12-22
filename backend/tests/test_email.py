"""
邮件功能测试模块

该模块测试系统的邮件相关功能:
- 密码重置邮件发送
- 密码更改通知邮件发送

主要测试:
    - 邮件发送功能
    - 邮件内容验证
    - 邮件接收者验证
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi_mail import FastMail

from backend.app.utils.email import email_manager

@pytest.mark.asyncio
async def test_send_reset_password_email():
    """测试发送密码重置邮件"""
    with patch.object(FastMail, 'send_message', new_callable=AsyncMock) as mock_send:
        email = "test@example.com"
        token = "test-token"
        
        await email_manager.send_reset_password_email(email, token)
        
        # 验证邮件发送
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        
        assert call_args.recipients == [email]
        assert "密码重置" in call_args.subject
        assert token in call_args.body

@pytest.mark.asyncio
async def test_send_password_changed_notification():
    """测试发送密码更改通知"""
    with patch.object(FastMail, 'send_message', new_callable=AsyncMock) as mock_send:
        email = "test@example.com"
        
        await email_manager.send_password_changed_notification(email)
        
        # 验证邮件发送
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0][0]
        
        assert call_args.recipients == [email]
        assert "密码已更改" in call_args.subject 