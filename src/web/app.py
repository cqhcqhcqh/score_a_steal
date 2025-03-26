#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Flask Web服务，用于提交批量搜索任务和查看任务进度
"""

import os
from flask import Flask, request, jsonify
from src.polling.app import app as celery_app
from src.polling.batch_search import batch_search, get_task_status

app = Flask(__name__)

# 存储任务信息的简单内存缓存
tasks_store = {}

@app.route('/')
def index():
    """首页，显示表单用于提交任务"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>闲鱼搜索任务管理</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input, textarea, select { width: 100%; padding: 8px; box-sizing: border-box; }
            button { padding: 10px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; }
            button:hover { background: #45a049; }
            .task-list { margin-top: 30px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            tr:hover { background-color: #f5f5f5; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>闲鱼搜索任务管理</h1>
            
            <div>
                <h2>创建新任务</h2>
                <form id="searchForm">
                    <div class="form-group">
                        <label for="keywords">关键词（多个关键词用逗号分隔）:</label>
                        <textarea id="keywords" name="keywords" rows="3" required>苹果14Pro256有锁</textarea>
                    </div>
                    <div class="form-group">
                        <label for="prices">期望价格（与关键词对应，多个用逗号分隔）:</label>
                        <input type="text" id="prices" name="prices" value=3000 placeholder="如: 5000,3000,2000", required>
                    </div>
                    <div class="form-group">
                        <label for="days">发布多少天内（单位是天，多个用逗号分隔）:</label>
                        <input type="text" id="days" name="days" value=2 placeholder="如: 2, 3, 1">
                    </div>
                    <div class="form-group">
                        <label for="webhook">飞书Webhook URL（可选）:</label>
                        <input type="text" id="webhook" value="https://open.feishu.cn/open-apis/bot/v2/hook/34e8583a-82e8-4b05-a1f5-6afce6cae815" name="webhook">
                    </div>
                    <div class="form-group">
                        <label for="headless">
                            <input type="checkbox" id="headless" name="headless" checked style="width: auto;"> 
                            无头模式（不显示浏览器窗口）
                        </label>
                    </div>
                    <button type="submit">提交任务</button>
                </form>
            </div>
            
            <div class="task-list">
                <h2>任务列表</h2>
                <table id="tasksTable">
                    <thead>
                        <tr>
                            <th>任务ID</th>
                            <th>关键词</th>
                            <th>状态</th>
                            <th>进度</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- 任务列表将通过JavaScript加载 -->
                    </tbody>
                </table>
            </div>
        </div>
        
        <script>
            // 页面加载时获取任务列表
            document.addEventListener('DOMContentLoaded', function() {
                loadTasks();
                
                // 设置定时更新
                setInterval(loadTasks, 5000);
                
                // 表单提交处理
                document.getElementById('searchForm').addEventListener('submit', function(e) {
                    e.preventDefault();
                    submitTask();
                });
            });
            
            // 加载任务列表
            function loadTasks() {
                fetch('/api/tasks')
                    .then(response => response.json())
                    .then(data => {
                        const tbody = document.querySelector('#tasksTable tbody');
                        tbody.innerHTML = '';
                        
                        if (data.tasks.length === 0) {
                            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">无任务</td></tr>';
                            return;
                        }
                        
                        data.tasks.forEach(task => {
                            const row = document.createElement('tr');
                            
                            // 任务ID
                            let cell = document.createElement('td');
                            cell.textContent = task.task_id;
                            row.appendChild(cell);
                            
                            // 关键词
                            cell = document.createElement('td');
                            cell.textContent = task.keywords.join(', ');
                            row.appendChild(cell);
                            
                            // 状态
                            cell = document.createElement('td');
                            cell.textContent = task.status.state || 'Unknown';
                            row.appendChild(cell);
                            
                            // 进度
                            cell = document.createElement('td');
                            if (task.status.total) {
                                const percent = Math.round((task.status.current / task.status.total) * 100);
                                cell.textContent = `${percent}% (${task.status.current}/${task.status.total})`;
                            } else {
                                cell.textContent = '待处理';
                            }
                            row.appendChild(cell);
                            
                            // 操作按钮
                            cell = document.createElement('td');
                            const detailsBtn = document.createElement('button');
                            detailsBtn.textContent = '详情';
                            detailsBtn.onclick = function() {
                                window.location.href = `/task/${task.task_id}`;
                            };
                            cell.appendChild(detailsBtn);

                            const terminateBtn = document.createElement('button');
                            terminateBtn.textContent = '终止';
                            terminateBtn.className = 'terminate-btn';
                            // 如果任务已完成或失败，则禁用终止按钮
                            terminateBtn.disabled = (task.status.state === 'SUCCESS' || task.status.state === 'FAILURE');
                            terminateBtn.onclick = function() {
                                if (confirm(`确定要终止任务 ${task.task_id} 吗？`)) {
                                     fetch(`/task/${task.task_id}/terminate`, {
                                            method: 'POST',
                                            headers: {
                                                'Content-Type': 'application/json',
                                            }
                                        })
                                        .then(response => response.json())
                                        .then(result => {
                                            alert(`ID: ${task.task_id} message: ${result.message}`);
                                            loadTasks();  // 刷新任务列表
                                        })
                                        .catch(error => {
                                            console.error('Error submitting task:', error);
                                            alert('终止任务时出错，请查看控制台');
                                        });
                                }
                            };
                            cell.appendChild(terminateBtn);

                            row.appendChild(cell);
                            
                            tbody.appendChild(row);
                        });
                    })
                    .catch(error => {
                        console.error('Error loading tasks:', error);
                    });
            }
            
            // 提交新任务
            function submitTask() {
                const keywords = document.getElementById('keywords').value.split(',').map(k => k.trim());
                const prices = document.getElementById('prices').value ? document.getElementById('prices').value.split(',').map(p => parseFloat(p.trim())) : [];
                const days = document.getElementById('days').value ? document.getElementById('days').value.split(',').map(p => parseFloat(p.trim())) : [];
                const webhook = document.getElementById('webhook').value.trim();
                const headless = document.getElementById('headless').checked;
                
                const data = {
                    keywords: keywords,
                    prices: prices.length > 0 ? prices : null,
                    days: days.length > 0 ? days : null,
                    webhook: webhook || null,
                    headless: headless
                };
                
                fetch('/api/tasks', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    alert(`任务已提交，ID: ${result.task_id}`);
                    loadTasks();  // 刷新任务列表
                })
                .catch(error => {
                    console.error('Error submitting task:', error);
                    alert('提交任务时出错，请查看控制台');
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/task/<task_id>')
def task_details(task_id):
    """任务详情页面"""
    task_info = tasks_store.get(task_id, {})
    status = get_task_status(task_id)
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>任务详情 - {task_id}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .info-card {{ background: #f9f9f9; padding: 15px; margin-bottom: 15px; border-radius: 5px; }}
            pre {{ background: #eee; padding: 10px; overflow-x: auto; }}
            .progress-bar {{ 
                height: 20px; 
                background-color: #e0e0e0; 
                border-radius: 4px; 
                margin-bottom: 10px;
            }}
            .progress {{ 
                height: 100%; 
                background-color: #4CAF50; 
                border-radius: 4px; 
                text-align: center;
                color: white;
                line-height: 20px;
            }}
            .back-btn {{
                display: inline-block;
                margin-top: 20px;
                padding: 8px 15px;
                background: #2196F3;
                color: white;
                text-decoration: none;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>任务详情</h1>
            
            <div class="info-card">
                <h2>基本信息</h2>
                <p><strong>任务ID:</strong> {task_id}</p>
                <p><strong>关键词:</strong> {', '.join(task_info.get('keywords', ['未知']))}</p>
                <p><strong>状态:</strong> <span id="taskState">{status.get('state', '未知')}</span></p>
            </div>
            
            <div class="info-card">
                <h2>进度</h2>
                <div class="progress-bar">
                    <div id="progressBar" class="progress" style="width: 0%">0%</div>
                </div>
                <p id="progressText">等待更新...</p>
            </div>
            
            <div class="info-card">
                <h2>详细状态</h2>
                <pre id="statusJson">正在加载...</pre>
            </div>
            
            <a href="/" class="back-btn">返回任务列表</a>
        </div>
        
        <script>
            // 更新任务状态
            function updateTaskStatus() {{
                fetch(`/api/tasks/{task_id}`)
                    .then(response => response.json())
                    .then(data => {{
                        // 更新状态
                        document.getElementById('taskState').textContent = data.state || '未知';
                        
                        // 更新进度条
                        let percent = 0;
                        let progressText = '等待处理...';
                        
                        if (data.total) {{
                            percent = Math.round((data.current / data.total) * 100);
                            progressText = `已处理: ${data.current}/${data.total} (${percent}%)`;
                            
                            if (data.status) {{
                                progressText += ` - ${data.status}`;
                            }}
                        }}
                        
                        document.getElementById('progressBar').style.width = `${{percent}}%`;
                        document.getElementById('progressBar').textContent = `${{percent}}%`;
                        document.getElementById('progressText').textContent = progressText;
                        
                        // 更新JSON状态
                        document.getElementById('statusJson').textContent = JSON.stringify(data, null, 2);
                        
                        // 如果任务完成，停止更新
                        if (data.state === 'SUCCESS' || data.state === 'FAILURE') {{
                            clearInterval(updateInterval);
                        }}
                    }})
                    .catch(error => {{
                        console.error('Error fetching task status:', error);
                        document.getElementById('statusJson').textContent = '获取状态时出错';
                    }});
            }}
            
            // 页面加载时更新一次
            document.addEventListener('DOMContentLoaded', updateTaskStatus);
            
            // 每3秒更新一次状态
            const updateInterval = setInterval(updateTaskStatus, 3000);
        </script>
    </body>
    </html>
    '''

@app.route('/task/<task_id>/terminate', methods=['POST'])
def terminate_task(task_id):
    try:
        # 这里添加实际的终止任务逻辑
        # terminate=True 相当于系统调用 kill -9
        celery_app.control.revoke(task_id, terminate=True)
        success = True  # 替换为实际终止结果
        if success:
            return jsonify({'success': True, 'message': '任务已终止'})
        else:
            return jsonify({'success': False, 'message': '无法终止任务'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """列出所有任务"""
    tasks_list = []
    for task_id, task_info in tasks_store.items():
        status = get_task_status(task_id)
        tasks_list.append({
            'task_id': task_id,
            'keywords': task_info.get('keywords', []),
            'status': status
        })
    return jsonify({'tasks': tasks_list})

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """获取任务状态"""
    return jsonify(get_task_status(task_id))

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """创建新任务"""
    data = request.json
    
    # 验证请求数据
    if not data or 'keywords' not in data or not data['keywords']:
        return jsonify({'error': '缺少关键词参数'}), 400
    
    # 创建批量搜索任务
    result = batch_search(
        data['keywords'],
        expected_prices=data.get('prices'),
        in_days=data.get('days'),
        feishu_webhook=data.get('webhook'),
        headless=data.get('headless', True),
        async_mode=True
    )
    
    # 保存任务信息到内存缓存
    task_id = result['task_id']
    tasks_store[task_id] = {
        'keywords': data['keywords'],
        'prices': data.get('prices'),
        'webhook': data.get('webhook'),
        'created_at': os.path.getmtime(__file__)  # 使用文件修改时间作为创建时间
    }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8119, use_reloader=False) 