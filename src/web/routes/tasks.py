from flask import Blueprint, jsonify, request, render_template
from src.model.queryParam import QueryModel, QueryModelFactory
from src.web.tasks import create_search_task, get_all_tasks, terminate_task, get_task_status, tasks_store

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks', methods=['GET'])
def list_tasks():
    return jsonify({'tasks': get_all_tasks()})

@tasks_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    return jsonify(get_task_status(task_id))

@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    if not data or 'keyword' not in data or not data['keyword']:
        return jsonify({'error': '缺少关键词参数'}), 400
    
    queryParams = QueryModel(keyword=data.get('keyword'), 
                             average_price=data.get('averagePrice'),
                             expected_price=data.get('expectedPrice'),
                             within_days=data.get('days'),
                             notify_webhook_url=data.get('webhook'))
    result = create_search_task(queryParams, 
                                headless=data.get('headless', True))
    return jsonify(result)

@tasks_bp.route('/tasks/<task_id>/terminate', methods=['POST'])
def terminate_task_route(task_id):
    return jsonify(terminate_task(task_id))

@tasks_bp.route('/task/<task_id>')
def task_details(task_id):
    task_info = tasks_store.get(task_id, {})
    status = get_task_status(task_id)
    return render_template('task_details.html', task_id=task_id, task_info=task_info, status=status)