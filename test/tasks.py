from celery import shared_task, states
from src.celery.app import app

@app.task(bind=True)
def test_batch_search_task(self, keywords):
    print(f"Task received: {keywords}")
    return "Task completed"