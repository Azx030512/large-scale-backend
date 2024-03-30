# 使用官方的 Python 基础镜像
FROM python:latest

# 设置工作目录
WORKDIR /flask_server

# 复制项目文件到工作目录
COPY . .

# 安装项目依赖
RUN pip install -r requirements.txt

# 暴露 Flask 应用程序的端口
EXPOSE 5000
EXPOSE 5001
EXPOSE 5002

# 启动 Flask 应用
CMD ["python", "run.py"]
