from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Employee, Request
from models import Base
from generate_data import generate_employees, generate_requests
from service import RequestService
from optimization import run_optimization_demo
import random

def main():
    engine = create_engine('sqlite:///requests.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    if session.query(Employee).count() == 0:
        print("Генерация сотрудников...")
        employees = generate_employees(session, 1000)
        print("Генерация заявок (1 млн)...")
        generate_requests(session, employees, 1_000_000)
    else:
        print("Данные уже существуют")
        employees = session.query(Employee).all()

    print("\n--- Примеры работы ---")
    req = session.query(Request).first()
    if req:
        print(f"Заявка #{req.id}, статус: {req.status}")

        success = RequestService.change_status(session, req.id, 'in_progress')
        print(f"Перевод в 'in_progress': {success}")

        success2 = RequestService.change_status(session, req.id, 'done')
        print(f"Перевод из 'in_progress' в 'done': {success2} (должен быть True)")

        new_req = session.query(Request).filter(Request.status == 'new').first()
        if new_req:
            success3 = RequestService.change_status(session, new_req.id, 'done')
            print(f"Перевод new->done: {success3} (должен быть False)")

    print("\nФильтрация: просроченные в работе у первого исполнителя")
    executor = employees[0]
    overdue_in_progress = RequestService.filter_requests(
        session, status='in_progress', executor_id=executor.id, overdue_only=True
    )
    print(f"Найдено: {len(overdue_in_progress)}")

    report = RequestService.get_report(session)
    print("\nОтчёт:")
    print("По статусам:", report['status_counts'])
    print("Просроченных всего:", report['overdue_count'])
    print("Выполненных по исполнителям (первые 5):", report['done_by_executor'][:5])

    print("\n--- Замеры производительности ---")
    run_optimization_demo(engine)

if __name__ == '__main__':
    main()
