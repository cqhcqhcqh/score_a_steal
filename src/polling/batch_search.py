#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量搜索工具，支持一次搜索多个关键词
使用连接池优化数据库操作
支持Celery后台任务和进度追踪
"""

import time
import json
import argparse
from celery import states
from src.polling.app import app
from celery.exceptions import Ignore
from src.qr_login import login_with_qr
from src.model.queryParam import QueryModel
from seleniumwire import webdriver as wire_webdriver
from selenium.webdriver.chrome.options import Options
from src.logger.app_logger import app_logger as logger

def setup_driver(headless=False):
    """配置浏览器驱动"""
    wire_options = {
        'disable_encoding': True,  # 不对请求/响应体进行编码
    }
    
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36')
    
    # 创建 Chrome 驱动
    driver = wire_webdriver.Chrome(
        options=chrome_options,
        seleniumwire_options=wire_options
    )
    driver.set_page_load_timeout(30)
    return driver

from functools import wraps
def repeat_every_5_minutes(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        while True:  # 检查任务是否被撤销
            func(self, *args, **kwargs)
            logger.info(f'{func} 任务执行一次结束....')
            for i in range(60):  # 5分钟 = 300秒
                logger.info(f'{func} 任务休眠中... 持续...{(i+1) * 5} 秒')
                time.sleep(5)
            logger.info(f'{func} 任务开启一次轮询....')
    return wrapper

@app.task(bind=True)
@repeat_every_5_minutes
def batch_search_task(self, 
                      data,
                      headless=True):
    
    return _batch_search_task(self,
                              QueryModel(**data),
                              headless)

def _batch_search_task(task, 
                       queryParams,
                       headless=True):
    """
    批量搜索多个关键词并保存结果的Celery任务
    
    参数:
    keywords - 要搜索的关键词列表
    expected_prices - 对应每个关键词的期望价格列表(可选)
    feishu_webhook - 飞书通知webhook地址(可选)
    headless - 是否使用无头模式
    """
    try:

        # 设置初始进度
        task.update_state(
            state=states.STARTED,
            meta={
                'current': 1,
                'total': 1,
                'status': 'Started batch search',
            }
        )
        
        try:
            # 获取当前关键词的参数
            keyword = queryParams.keyword
            logger.info(f'queryParams: {queryParams}')
            
            try:
                # 更新任务状态
                task.update_state(
                    state=states.STARTED,
                    meta={
                        'current': 1,
                        'total': 1,
                        'keyword': keyword,
                        'status': f'Processing {keyword}',
                    }
                )
                
                # 搜索并处理结果
                login_with_qr(queryParams,
                              headless=headless)
                
                # 更新任务状态
                task.update_state(
                    state='PROGRESS',
                    meta={
                        'current': 1,
                        'total': 1,
                        'keyword': keyword,
                        'status': f'Processed {keyword} item)',
                    }
                )
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.info(f"处理关键词 '{keyword}' 时出错: {str(e)}")
                # 返回首页，尝试继续下一个关键词
                time.sleep(2)
            
            logger.info(f"\n搜索完成，共处理 {keyword} 个商品")
            
            # 任务完成
            return {
                'current': 1,
                'total': 1,
                'status': 'Task completed!',
                'keywords': keyword,
                'success': True
            }
            
        finally:
            # 关闭浏览器
            # driver.quit()
            pass
            
    except Exception as e:
        # 任务出错
        task.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e),
                'status': 'Task failed',
                'success': False
            }
        )
        raise Ignore()
    
def batch_search(queryParams, 
                 headless=True,
                 async_mode=True):
    """
    批量搜索工具入口函数，支持同步/异步模式
    
    参数:
    keywords - 要搜索的关键词列表
    expected_prices - 对应每个关键词的期望价格列表(可选)
    feishu_webhook - 飞书通知webhook地址(可选)
    headless - 是否使用无头模式
    async_mode - 是否使用异步模式(Celery)
    
    返回:
    异步模式: Celery任务ID
    同步模式: 搜索结果
    """
    if async_mode:
        # 使用Celery异步执行
        task = batch_search_task.delay(queryParams.to_dict(),
                                       headless=headless)
        return {
            'task_id': task.id,
            'status': 'Task scheduled',
            'keywords': queryParams.keyword
        }
    else:
        # 直接执行(同步)
        return batch_search_task(queryParams,
                                 headless=headless)

def get_task_status(task_id):
    """
    获取Celery任务状态
    
    参数:
    task_id - Celery任务ID
    
    返回:
    任务状态信息
    """
    task = batch_search_task.AsyncResult(task_id)
    if task.state == states.PENDING:
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state == states.STARTED:
        response = {
            'state': task.state,
            'status': 'Started...',
            'meta': task.info
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
    elif task.state == states.SUCCESS:
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', ''),
        }
    elif task.state == states.FAILURE:
        # 任务失败
        response = {
            'state': task.state,
            'status': 'Error',
            'message': str(task.info)  # 错误信息
        }
    else:
        # 其他状态
        response = {
            'state': task.state,
            'status': f'Unknown state: {task.state}'
        }
    
    return response

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='批量搜索闲鱼商品并保存数据')
    parser.add_argument('keywords', nargs='+', help='要搜索的关键词，可提供多个')
    parser.add_argument('--prices', nargs='+', type=float, help='对应每个关键词的期望价格')
    parser.add_argument('--headless', action='store_true', help='启用无头模式')
    parser.add_argument('--webhook', help='飞书机器人Webhook地址')
    parser.add_argument('--async', dest='async_mode', action='store_true', help='使用Celery异步执行')
    parser.add_argument('--task-id', help='获取指定ID的任务状态')
    
    args = parser.parse_args()
    
    # 获取任务状态
    if args.task_id:
        status = get_task_status(args.task_id)
        logger.info(json.dumps(status, indent=2))
        return
    
    # 执行批量搜索
    result = batch_search(
        args.keywords, 
        expected_prices=args.prices,
        in_days=args.days,
        feishu_webhook=args.webhook,
        headless=args.headless,
        async_mode=args.async_mode
    )
    
    if args.async_mode:
        logger.info(f"任务已排队，任务ID: {result['task_id']}")
        logger.info(f"使用以下命令查看任务状态:")
        logger.info(f"python batch_search.py --task-id {result['task_id']}")
    else:
        logger.info(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 