from app.worker.celery_app import celery_app


@celery_app.task
def test_task():
    return "MemoGraph Celery worker is working"