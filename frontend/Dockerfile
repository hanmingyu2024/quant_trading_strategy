# 开发环境
FROM node:18-alpine

WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 启动开发服务器
CMD ["npm", "run", "dev"]

EXPOSE 3000

# 生产阶段
FROM nginx:alpine

# 复制构建产物到 Nginx
COPY --from=build /app/build /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"] 