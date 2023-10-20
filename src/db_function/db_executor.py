import sqlite3
from time import sleep
from random import randint

from src.log import setup_logger

log = setup_logger(__name__)

def execute(conn: sqlite3.Connection, sql_statement: str, param: tuple, task_name: str = 'unknown'):
    cursor = conn.cursor()
    for retry in range(5):
        try:
            cursor.execute(sql_statement, param)
            conn.commit()
        except:
            waiting = randint(1, 5)
            log.info(f'in task {task_name}: the database is locked, try again in {waiting} seconds, number of retries: {retry}')
            sleep(waiting)