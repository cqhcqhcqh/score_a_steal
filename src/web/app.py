#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from flask import Flask
from src.web.config import Config
from src.web.routes.home import home_bp
from src.web.routes.tasks import tasks_bp
from src.polling.app import app as celery_app

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'routes', 'templates'))
    app.config.from_object(Config)
    
    # 注册蓝图
    app.register_blueprint(home_bp)
    app.register_blueprint(tasks_bp, url_prefix='/api')
    
    # 初始化Celery
    app.celery = celery_app
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT,
        use_reloader=False
    )