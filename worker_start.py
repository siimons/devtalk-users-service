from app.workers.celery import celery


if __name__ == "__main__":
    celery.start()