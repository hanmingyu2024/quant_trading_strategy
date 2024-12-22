from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

class TemplateManager:
    def __init__(self):
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def render_password_reset_email(self, username: str, token: str, expires_in: int) -> str:
        """渲染密码重置邮件"""
        template = self.env.get_template("email/password_reset.html")
        return template.render(
            username=username,
            token=token,
            expires_in=expires_in,
            year=datetime.now().year
        )

    def render_password_reset_success_email(
        self,
        username: str,
        reset_time: datetime,
        ip_address: str,
        user_agent: str
    ) -> str:
        """渲染密码重置成功邮件"""
        template = self.env.get_template("email/password_reset_success.html")
        return template.render(
            username=username,
            reset_time=reset_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            ip_address=ip_address,
            user_agent=user_agent,
            year=datetime.now().year
        )

# 创建全局实例
template_manager = TemplateManager() 