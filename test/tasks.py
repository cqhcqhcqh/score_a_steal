from celery import shared_task, states
from src.polling.app import app
from src.logger.app_logger import app_logger as logger

@app.task(bind=True)
def test_batch_search_task(self, keywords):
    logger.info(f"Task received: {keywords}")
    return "Task completed"