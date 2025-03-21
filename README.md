# 闲鱼好价推荐系统

一个基于Celery的闲鱼商品搜索和推荐系统，可以自动搜索、评估商品和卖家，并通过飞书机器人推送优质商品。

## 特性

- 基于Celery的异步任务系统，支持后台批量处理
- 通过Web界面管理和监控搜索任务
- 卖家可信度评估
- 引流商家自动检测
- 商品匹配度评分
- 飞书机器人通知

## 系统要求

- Python 3.7+
- Redis (用于Celery消息队列)
- Chrome浏览器和对应版本的ChromeDriver

## 安装

1. 克隆代码库
```bash
git clone <仓库地址>
cd score_a_steal
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动Redis (如未安装)
```bash
# MacOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
```

## 使用方法

### 方法1: 使用启动脚本

```bash
chmod +x start.sh
./start.sh
```

脚本会自动启动Celery Worker和Web服务器。

### 方法2: 手动启动

1. 启动Celery Worker
```bash
cd src
celery -A celery_app worker --loglevel=info
```

2. 启动Web服务
```bash
cd <项目根目录>
python -m src.web_server
```

3. 访问Web界面
打开浏览器访问: http://localhost:8119

### 命令行使用

也可以通过命令行直接使用批量搜索功能:

```bash
# 异步模式（Celery任务）
python -m src.batch_search "iPhone 14 Pro" "MacBook Pro" --prices 5000 8000 --async

# 查看任务状态
python -m src.batch_search --task-id <任务ID>
```

## 系统架构

- `src/celery_app.py`: Celery配置
- `src/batch_search.py`: 批量搜索功能和Celery任务
- `src/seller_evaluation.py`: 卖家评估和商品匹配度计算
- `src/notifier.py`: 飞书通知和控制台输出
- `src/web_server.py`: Web界面和API
- `src/filter_by_keyword.py`: 关键词搜索和数据爬取
- `src/deal_recommendation.py`: 推荐系统核心

## 飞书通知配置

1. 在飞书中创建一个自定义机器人
2. 获取Webhook URL
3. 在Web界面或命令行参数中提供Webhook URL 