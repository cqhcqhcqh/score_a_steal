from src.polling.batch_search import batch_search, get_task_status
import os

# 任务存储
tasks_store = {}

def create_search_task(queryParams, headless=True):
    result = batch_search(queryParams, 
                          headless=headless,
                          async_mode=True)
    
    task_id = result['task_id']
    tasks_store[task_id] = {
        'keywords': queryParams.keyword,
        'prices': queryParams.expected_price,
        'webhook': queryParams.notify_webhook_url,
        'created_at': os.path.getmtime(__file__)
    }
    return result

def get_all_tasks():
    return [
        {
            'task_id': task_id,
            'keywords': info.get('keywords', []),
            'status': get_task_status(task_id)
        }
        for task_id, info in tasks_store.items()
    ]

def terminate_task(app, task_id):
    try:
        app.celery.control.revoke(task_id, terminate=True)
        return {'success': True, 'message': '任务已终止'}
    except Exception as e:
        return {'success': False, 'message': str(e)}