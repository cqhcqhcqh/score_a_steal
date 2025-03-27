# from celery import Celery
# from celery.result import AsyncResult
# import time
# from logger.app_logger import app_logger as logger

# app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# @app.task
# def add(x, y):
#     for i in range(0, 10):
#         logger.info(f'add: {i}')
#         time.sleep(1)
#     return x + y

# # 提交任务
# task = add.delay(4, 6)
# task_id = task.id

# # 检查状态
# result = AsyncResult(task_id, app=app)
# logger.info(f"任务状态: {result.state}")

# time.sleep(5)
# # 撤销任务
# app.control.revoke(task_id, terminate=True)

# # 再次检查状态
# result = AsyncResult(task_id, app=app)
# if result.state == 'REVOKED':
#     logger.info("任务已被撤销")
# else:
#     logger.info(f"再次查询任务状态: {result.state}")