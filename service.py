from sqlalchemy.orm import Session
from models import Request, Employee
from datetime import datetime


class RequestService:
    ALLOWED_TRANSITIONS = {
        'new': ['in_progress'],
        'in_progress': ['done'],
        'done': []
    }

    @staticmethod
    def change_status(session: Session, request_id: int, new_status: str) -> bool:
        request = session.query(Request).filter(Request.id == request_id).first()
        if not request:
            return False
        if new_status not in RequestService.ALLOWED_TRANSITIONS.get(request.status, []):
            return False
        request.status = new_status
        session.commit()
        return True

    @staticmethod
    def change_executor(session: Session, request_id: int, new_executor_id: int) -> bool:
        request = session.query(Request).filter(Request.id == request_id).first()
        if not request:
            return False
        if request.status == 'done':
            return False
        request.executor_id = new_executor_id
        session.commit()
        return True

    @staticmethod
    def filter_requests(session: Session, status=None, executor_id=None, department=None, overdue_only=False):
        query = session.query(Request)
        if status:
            query = query.filter(Request.status == status)
        if executor_id:
            query = query.filter(Request.executor_id == executor_id)
        if department:
            query = query.join(Employee, Request.executor_id == Employee.id).filter(Employee.department == department)
        if overdue_only:
            query = query.filter(Request.deadline < datetime.now())
        return query.all()

    @staticmethod
    def get_report(session: Session):
        from sqlalchemy import func
        status_counts = session.query(Request.status, func.count()).group_by(Request.status).all()
        overdue_count = session.query(Request).filter(Request.deadline < datetime.now()).count()

        done_by_executor = session.query(
            Employee.full_name,
            func.count(Request.id)
        ).join(Request, Request.executor_id == Employee.id).filter(Request.status == 'done').group_by(Employee.id).all()
        return {
            'status_counts': status_counts,
            'overdue_count': overdue_count,
            'done_by_executor': done_by_executor
        }
