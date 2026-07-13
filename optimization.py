import time
from sqlalchemy import create_engine, Index
from sqlalchemy.orm import sessionmaker
from models import Request, Employee
from datetime import datetime


def measure_query(session, executor_id):
    start = time.time()
    result = session.query(Request).filter(
        Request.executor_id == executor_id,
        Request.status == 'in_progress',
        Request.deadline < datetime.now()
    ).order_by(Request.deadline).all()
    elapsed = time.time() - start
    return elapsed, len(result)


def run_optimization_demo(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    executor = session.query(Employee).first()
    if not executor:
        print("Нет сотрудников")
        return

    print("Замер до оптимизации (без индекса)")
    elapsed, count = measure_query(session, executor.id)
    print(f"Время: {elapsed:.4f} сек, найдено заявок: {count}")

    print("Создаём индекс на (executor_id, status, deadline)")
    idx = Index('idx_executor_status_deadline', Request.executor_id, Request.status, Request.deadline)
    idx.create(engine, checkfirst=True)

    print("Замер после оптимизации")
    elapsed2, count2 = measure_query(session, executor.id)
    print(f"Время: {elapsed2:.4f} сек, найдено заявок: {count2}")

    print(f"Ускорение: {elapsed / elapsed2:.2f}x")