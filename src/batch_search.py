#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量搜索工具，支持一次搜索多个关键词
使用连接池优化数据库操作
支持Celery后台任务和进度追踪
"""

import sys
import time
import argparse
import json
from celery import shared_task, states
from celery.exceptions import Ignore
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver as wire_webdriver
from filter_by_keyword import filter_by_keyword_lastest
from db_manager import db_manager
from save_filtered_result import Base
from celery_app import app

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

@shared_task(bind=True)
def batch_search_task(self, keywords, expected_prices=None, product_types=None, feishu_webhook=None, base_url="https://www.goofish.com", headless=True):
    """
    批量搜索多个关键词并保存结果的Celery任务
    
    参数:
    keywords - 要搜索的关键词列表
    expected_prices - 对应每个关键词的期望价格列表(可选)
    product_types - 对应每个关键词的产品类型列表(可选)
    feishu_webhook - 飞书通知webhook地址(可选)
    base_url - 闲鱼网站URL
    headless - 是否使用无头模式
    """
    try:
        # 确保数据库表已创建
        db_manager.create_all_tables(Base)
        
        # 初始化浏览器
        driver = setup_driver(headless)
        
        # 初始化进度信息
        total_keywords = len(keywords)
        processed_keywords = 0
        found_items = []
        
        # 设置初始进度
        self.update_state(
            state=states.STARTED,
            meta={
                'current': 0,
                'total': total_keywords,
                'status': 'Started batch search',
                'found_items': 0
            }
        )
        
        try:
            # 访问闲鱼首页
            driver.get(base_url)
            time.sleep(3)  # 等待页面加载
            
            total_processed = 0
            print(f"开始批量搜索，共 {total_keywords} 个关键词")
            
            # 循环处理每个关键词
            for i, keyword in enumerate(keywords):
                # 获取当前关键词的参数
                expected_price = None if expected_prices is None else expected_prices[i] if i < len(expected_prices) else None
                product_type = 'iPhone' if product_types is None else product_types[i] if i < len(product_types) else 'iPhone'
                
                print(f"\n=== [{i+1}/{total_keywords}] 搜索关键词: {keyword} ===")
                if expected_price:
                    print(f"期望价格: {expected_price}, 产品类型: {product_type}")
                
                try:
                    # 更新任务状态
                    self.update_state(
                        state=states.STARTED,
                        meta={
                            'current': i,
                            'total': total_keywords,
                            'keyword': keyword,
                            'status': f'Processing {keyword}',
                            'found_items': len(found_items)
                        }
                    )
                    
                    # 搜索并处理结果
                    processed = filter_by_keyword_lastest(
                        driver, 
                        keyword, 
                        expected_price=expected_price,
                        product_type=product_type,
                        feishu_webhook=feishu_webhook
                    )
                    
                    total_processed += processed
                    processed_keywords += 1
                    
                    # 更新任务状态
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': processed_keywords,
                            'total': total_keywords,
                            'keyword': keyword,
                            'status': f'Processed {keyword} ({processed} items)',
                            'found_items': len(found_items)
                        }
                    )
                    
                    # 返回首页继续下一次搜索
                    driver.get(base_url)
                    time.sleep(2)
                except Exception as e:
                    print(f"处理关键词 '{keyword}' 时出错: {str(e)}")
                    # 返回首页，尝试继续下一个关键词
                    driver.get(base_url)
                    time.sleep(2)
                    continue
            
            print(f"\n批量搜索完成，共处理 {total_processed} 个商品")
            
            # 任务完成
            return {
                'current': total_keywords,
                'total': total_keywords,
                'status': 'Task completed!',
                'found_items': len(found_items),
                'total_processed': total_processed,
                'keywords': keywords,
                'success': True
            }
            
        finally:
            # 关闭浏览器
            driver.quit()
            
    except Exception as e:
        # 任务出错
        self.update_state(
            state=states.FAILURE,
            meta={
                'exc_type': type(e).__name__,
                'exc_message': str(e),
                'status': 'Task failed',
                'success': False
            }
        )
        raise Ignore()

def batch_search(keywords, expected_prices=None, product_types=None, feishu_webhook=None, base_url="https://www.goofish.com", headless=False, async_mode=True):
    """
    批量搜索工具入口函数，支持同步/异步模式
    
    参数:
    keywords - 要搜索的关键词列表
    expected_prices - 对应每个关键词的期望价格列表(可选)
    product_types - 对应每个关键词的产品类型列表(可选)
    feishu_webhook - 飞书通知webhook地址(可选)
    base_url - 闲鱼网站URL
    headless - 是否使用无头模式
    async_mode - 是否使用异步模式(Celery)
    
    返回:
    异步模式: Celery任务ID
    同步模式: 搜索结果
    """
    if async_mode:
        # 使用Celery异步执行
        task = batch_search_task.delay(
            keywords, 
            expected_prices=expected_prices,
            product_types=product_types,
            feishu_webhook=feishu_webhook,
            base_url=base_url,
            headless=headless
        )
        return {
            'task_id': task.id,
            'status': 'Task scheduled',
            'keywords': keywords
        }
    else:
        # 直接执行(同步)
        return batch_search_task(
            None,  # self参数在直接调用时不需要
            keywords, 
            expected_prices=expected_prices,
            product_types=product_types,
            feishu_webhook=feishu_webhook,
            base_url=base_url,
            headless=headless
        )

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
            'found_items': task.info.get('found_items', 0),
            'total_processed': task.info.get('total_processed', 0)
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
    parser.add_argument('--types', nargs='+', help='对应每个关键词的产品类型，默认为iPhone')
    parser.add_argument('--headless', action='store_true', help='启用无头模式')
    parser.add_argument('--url', default='https://www.goofish.com', help='闲鱼网站URL')
    parser.add_argument('--webhook', help='飞书机器人Webhook地址')
    parser.add_argument('--async', dest='async_mode', action='store_true', help='使用Celery异步执行')
    parser.add_argument('--task-id', help='获取指定ID的任务状态')
    
    args = parser.parse_args()
    
    # 获取任务状态
    if args.task_id:
        status = get_task_status(args.task_id)
        print(json.dumps(status, indent=2))
        return
    
    # 执行批量搜索
    result = batch_search(
        args.keywords, 
        expected_prices=args.prices,
        product_types=args.types,
        feishu_webhook=args.webhook,
        base_url=args.url, 
        headless=args.headless,
        async_mode=args.async_mode
    )
    
    if args.async_mode:
        print(f"任务已排队，任务ID: {result['task_id']}")
        print(f"使用以下命令查看任务状态:")
        print(f"python batch_search.py --task-id {result['task_id']}")
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 