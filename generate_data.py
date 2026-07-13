from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Employee, Request
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('ru_RU')


def generate_employees(session, count=1000):
    departments = ['IT', 'HR', 'Sales', 'Marketing', 'Finance', 'Legal', 'R&D']
    positions = ['Junior', 'Middle', 'Senior', 'Lead', 'Manager', 'Director']
    employees = []
    for _ in range(count):
        emp = Employee(
            full_name=fake.name(),
            department=random.choice(departments),
            position=random.choice(positions)
        )
        employees.append(emp)
    session.add_all(employees)
    session.commit()
    return employees


def generate_requests(session, employees, count=1_000_000):
    batch_size = 10000
    statuses = ['new', 'in_progress', 'done']

    weights = [0.1, 0.3, 0.6]
    for i in range(0, count, batch_size):
        batch = []
        for _ in range(batch_size):
            author = random.choice(employees)
            executor = random.choice(employees)

            while executor == author:
                executor = random.choice(employees)
            created = fake.date_time_between(start_date='-1y', end_date='now')
            deadline = created + timedelta(days=random.randint(1, 30))

            status = random.choices(statuses, weights=weights)[0]

            req = Request(
                number=fake.unique.random_number(digits=10),
                created_date=created,
                author_id=author.id,
                executor_id=executor.id,
                description=fake.text(max_nb_chars=200),
                deadline=deadline,
                status=status
            )
            batch.append(req)
        session.add_all(batch)
        session.commit()
        print(f'Generated {i+batch_size} requests')