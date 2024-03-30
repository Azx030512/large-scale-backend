# 使用官方 MySQL 镜像作为基础镜像
FROM mysql:8

# 设置数据库的环境变量
ENV MYSQL_ROOT_PASSWORD=azx
ENV MYSQL_DATABASE=mqtt
# ENV MYSQL_USER=root
# ENV MYSQL_PASSWORD=azx
# ENV MYSQL_ROOT_PASSWORD = azx

# 将本地的初始化 SQL 文件复制到容器中
COPY ./init.sql /docker-entrypoint-initdb.d/

# 暴露 MySQL 默认端口
EXPOSE 3306
