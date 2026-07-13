from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False)

    requests_created = relationship('Request', foreign_keys='Request.author_id', backref='author')
    requests_executed = relationship('Request', foreign_keys='Request.executor_id', backref='executor')


class Request(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    number = Column(String(20), unique=True, nullable=False)
    created_date = Column(DateTime, default=datetime.now)
    author_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    executor_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    description = Column(String(500))
    deadline = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default='new')

    __table_args__ = (
        CheckConstraint("status IN ('new', 'in_progress', 'done')", name='check_status'),
    )
