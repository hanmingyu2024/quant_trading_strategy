@echo off
echo 设置数据库维护计划任务...

:: 创建每周维护任务
schtasks /create /tn "DB_Weekly_Maintenance" /tr "python maintain_database.py" /sc weekly /d SUN /st 00:00

:: 创建每日备份任务
schtasks /create /tn "DB_Daily_Backup" /tr "python backup_database.py" /sc daily /st 01:00

echo 计划任务设置完成！