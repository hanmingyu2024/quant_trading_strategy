import os
from datetime import datetime

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def create_file(path, content=""):
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created file: {path}")

def setup_advanced_structure():
    # 项目根目录
    root_dir = "quant_trading_strategy"
    create_directory(root_dir)
    
    # 主要目录结构
    dirs = [
        'api_gateway/configs',
        'api_gateway/routes',
        'backend/app/cache',
        'backend/app/queue',
        'message_queue/kafka/config',
        'message_queue/rabbitmq/config',
        'cache/redis/config',
        'cache/redis-cluster'
    ]
    
    for dir_path in dirs:
        full_path = os.path.join(root_dir, dir_path)
        create_directory(full_path)

    # 创建基础配置文件
    base_files = {
        'api_gateway/configs/nginx.conf': '''
server {
    listen 80;
    server_name localhost;
    
    location /api {
        proxy_pass http://backend:8000;
    }
}
''',
        
        'api_gateway/configs/kong.yml': '''
_format_version: "2.1"
services:
  - name: trading-api
    url: http://backend:8000
    routes:
      - name: api-route
        paths:
          - /api
''',
        
        'cache/redis/config/redis.conf': '''
bind 0.0.0.0
port 6379
maxmemory 256mb
maxmemory-policy allkeys-lru
''',
        
        'message_queue/kafka/config/server.properties': '''
broker.id=1
listeners=PLAINTEXT://:9092
log.dirs=/var/lib/kafka/data
zookeeper.connect=zookeeper:2181
'''
    }

    for file_path, content in base_files.items():
        full_path = os.path.join(root_dir, file_path)
        create_file(full_path, content)

    # 创建 Dockerfile 文件
    dockerfiles = {
        'api_gateway/Dockerfile': '''FROM nginx:alpine
COPY configs/nginx.conf /etc/nginx/conf.d/default.conf
''',
        
        'cache/redis/Dockerfile': '''FROM redis:7.0
COPY config/redis.conf /etc/redis/redis.conf
CMD ["redis-server", "/etc/redis/redis.conf"]
''',
        
        'message_queue/kafka/Dockerfile': '''FROM confluentinc/cp-kafka:7.0.0
COPY config/server.properties /etc/kafka/server.properties
'''
    }

    for file_path, content in dockerfiles.items():
        full_path = os.path.join(root_dir, file_path)
        create_file(full_path, content)

if __name__ == "__main__":
    setup_advanced_structure() 