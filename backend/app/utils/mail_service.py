"""
邮件服务模块
处理邮件发送和管理
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
import threading
import queue
from backend.app.core.config import settings

class EmailManager:
    """邮件管理器"""
    
    def __init__(self):
        """初始化邮件管理器"""
        # SMTP配置
        self.host = settings.SMTP_HOST  # 使用SMTP_HOST而不是SMTP_SERVER
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        
        # 统计信息
        self.sent_count = 0
        self.failed_count = 0
        self.last_sent = None
        self.hourly_stats = [0] * 24
        
        # 线程安全的队列
        self.email_queue = queue.Queue()
        self.is_processing = False
        self.lock = threading.Lock()
        
        # 启动处理线程
        self.start_processing()
    
    def connect_smtp(self) -> smtplib.SMTP:
        """创建SMTP连接"""
        try:
            if settings.SMTP_USE_SSL:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=settings.SMTP_TIMEOUT)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=settings.SMTP_TIMEOUT)
                
            if settings.SMTP_USE_TLS:
                server.starttls()
                
            if self.username and self.password:
                server.login(self.username, self.password)
                
            return server
            
        except Exception as e:
            print(f"SMTP连接失败: {str(e)}")
            raise
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html: Optional[str] = None,
        priority: bool = False
    ) -> bool:
        """
        发送邮件
        
        Args:
            to_emails: 收件人列表
            subject: 邮件主题
            body: 邮件正文
            html: HTML格式正文
            priority: 是否优先处理
            
        Returns:
            bool: 是否成功加入队列
        """
        try:
            email_data = {
                "to_emails": to_emails,
                "subject": subject,
                "body": body,
                "html": html,
                "timestamp": datetime.now()
            }
            
            if priority:
                self.email_queue.put((0, email_data))  # 优先级队列
            else:
                self.email_queue.put((1, email_data))
                
            return True
            
        except Exception as e:
            print(f"添加邮件到队列失败: {str(e)}")
            return False
    
    def process_email(self, email_data: dict) -> bool:
        """处理单个邮件"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = email_data['subject']
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ", ".join(email_data['to_emails'])
            
            # 添加文本内容
            msg.attach(MIMEText(email_data['body'], 'plain'))
            
            # 如果有HTML内容，也添加HTML版本
            if email_data.get('html'):
                msg.attach(MIMEText(email_data['html'], 'html'))
            
            # 发送邮件
            with self.connect_smtp() as server:
                server.send_message(msg)
            
            # 更新统计信息
            with self.lock:
                self.sent_count += 1
                self.last_sent = datetime.now()
                hour = self.last_sent.hour
                self.hourly_stats[hour] += 1
            
            return True
            
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
            with self.lock:
                self.failed_count += 1
            return False
    
    def start_processing(self):
        """启动邮件处理"""
        def process_queue():
            while True:
                try:
                    _, email_data = self.email_queue.get()
                    self.process_email(email_data)
                    self.email_queue.task_done()
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"处理邮件队列出错: {str(e)}")
        
        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        with self.lock:
            return {
                "sent_count": self.sent_count,
                "failed_count": self.failed_count,
                "last_sent": self.last_sent,
                "hourly_stats": self.hourly_stats.copy(),
                "queue_size": self.email_queue.qsize()
            }

# 创建全局邮件管理器实例
email_manager = EmailManager()

# 导出邮件管理器
__all__ = ['email_manager'] 