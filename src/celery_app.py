from celery import Celery
import os

# 设置默认的Django设置模块
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapp.settings')

# 创建Celery实例
app = Celery('score_a_steal')

# 设置broker（消息队列）和backend（存储结果）
# 这里使用Redis作为broker和backend，也可以使用其他的如RabbitMQ
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/1'

# 配置Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # 指定接受的内容类型
    result_serializer='json',
    timezone='Asia/Shanghai',  # 时区设置
    enable_utc=False,
    task_track_started=True,  # 追踪任务的开始状态
    task_time_limit=3600,  # 任务的硬时间限制（秒）
    worker_max_tasks_per_child=200,  # 每个worker执行多少个任务后自动重启
)

# 自动发现和注册任务
app.autodiscover_tasks(['src'])

if __name__ == '__main__':
    app.start() 