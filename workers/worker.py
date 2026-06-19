import dotenv
import logging
import os

if not os.getenv("REDIS_URI"):
    dotenv.load_dotenv()

from celery import Celery
from celery.signals import worker_process_init

import crud

app = Celery(
    "worker",
    broker=os.getenv("REDIS_URI"),
    backend=os.getenv("REDIS_URI")
)

@worker_process_init.connect
def configure_workers(*args, **kwargs):
    crud.init_db()

@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        int(os.getenv("EXP_TIME", 60*60*12)),
        remove_requests.s(),
        name="remove requests"
    )
    sender.add_periodic_task(
        int(os.getenv("EXP_TIME", 60*60*12)),
        remove_orphaned_days.s(),
        name="remove orphaned days"
    )
    sender.add_periodic_task(
        int(os.getenv("EXP_TIME", 60*60*12)),
        remove_orphaned_friends.s(),
        name="remove orphaned friends"
    )
    sender.add_periodic_task(
        int(os.getenv("EXP_TIME", 60*60*12)),
        update_user_references.s(),
        name="update user references"
    )


@app.task
def remove_requests():
    logging.info("remove_requests started")
    crud.remove_requests()
    logging.info("remove_requests finished")


@app.task
def remove_orphaned_days():
    logging.info("remove_orphaned_days started")
    crud.remove_orphaned_days()
    logging.info("remove_orphaned_days finished")


@app.task
def remove_orphaned_friends():
    logging.info("remove_orphaned_friends started")
    crud.remove_orphaned_friends()
    logging.info("remove_orphaned_friends finished")


@app.task
def update_user_references():
    logging.info("update_user_references started")
    crud.update_user_references()
    logging.info("update_user_references finished")
    

# celery -A worker.app worker --loglevel=info
# celery -A worker.app beat --loglevel=info