#!/bin/bash

# 启动脚本 - 启动Celery Worker和Web服务

# 设置基础目录
BASE_DIR=$(pwd)
SRC_DIR="$BASE_DIR/src"

# 确保有日志目录
mkdir -p logs

# 检查Redis是否运行
redis-cli ping
if [ $? -ne 0 ]; then
    echo "ERROR: Redis服务未运行，请先启动Redis"
    echo "可以使用以下命令启动Redis:"
    echo "  brew services start redis  # macOS"
    echo "  systemctl start redis      # Linux"
    exit 1
fi
echo "Redis 服务正常运行"

# 检查是否已安装依赖
pip list | grep -q "celery"
if [ $? -ne 0 ]; then
    echo "安装依赖..."
    pip install -r requirements.txt
fi

cd "$SRC_DIR"

# 启动Celery Worker
echo "启动Celery Worker..."
celery -A src.celery.app worker --loglevel=info --logfile="$BASE_DIR/logs/celery.log" --detach

# 等待Worker启动
sleep 2

# 启动Web服务
echo "启动Web服务..."
cd "$BASE_DIR"
gunicorn --bind 0.0.0.0:8119 --workers 2 --threads 4 --timeout 120 "src.flask:app" > logs/web.log 2>&1 &

# 显示访问信息
echo ""
echo "系统已启动!"
echo "Web服务：http://localhost:8119"
echo "日志位置："
echo "  Celery日志: logs/celery.log"
echo "  Web服务日志: logs/web.log"
echo ""
echo "使用以下命令停止服务："
echo "  pkill -f 'celery worker'"
echo "  pkill -f 'gunicorn'" 