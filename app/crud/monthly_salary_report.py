# app/crud/monthly_salary_report.py
from sqlalchemy.orm import Session, joinedload
from app.models.monthly_salary_report import MonthlySalaryReport
from app.schemas.monthly_salary_report import MonthlySalaryReportCreate, MonthlySalaryReportUpdate
from typing import List, Optional
from datetime import datetime

def get_salary_report(db: Session, report_id: int) -> Optional[MonthlySalaryReport]:
    return db.query(MonthlySalaryReport).options(joinedload(MonthlySalaryReport.employee)).filter(MonthlySalaryReport.report_id == report_id).first()

def get_salary_reports(db: Session, skip: int = 0, limit: int = 100):
    return db.query(MonthlySalaryReport).offset(skip).limit(limit).all()

def get_salary_reports_by_employee(db: Session, employee_id: int) -> List[MonthlySalaryReport]:
    return db.query(MonthlySalaryReport).options(joinedload(MonthlySalaryReport.employee)).filter(MonthlySalaryReport.employee_id == employee_id).all()

def get_salary_reports_by_month(db: Session, month_year: str) -> List[MonthlySalaryReport]:
    return db.query(MonthlySalaryReport).options(joinedload(MonthlySalaryReport.employee)).filter(MonthlySalaryReport.month_year == month_year).all()

def create_salary_report(db: Session, salary_report: MonthlySalaryReportCreate) -> MonthlySalaryReport:
    db_salary_report = MonthlySalaryReport(**salary_report.dict(), generated_date=datetime.now())
    db.add(db_salary_report)
    db.commit()
    db.refresh(db_salary_report)
    return db_salary_report

def update_salary_report(db: Session, report_id: int, salary_report: MonthlySalaryReportUpdate) -> Optional[MonthlySalaryReport]:
    db_salary_report = db.query(MonthlySalaryReport).filter(MonthlySalaryReport.report_id == report_id).first()
    if db_salary_report:
        for key, value in salary_report.dict(exclude_unset=True).items():
            setattr(db_salary_report, key, value)
        db.commit()
        db.refresh(db_salary_report)
    return db_salary_report

def delete_salary_report(db: Session, report_id: int) -> bool:
    db_salary_report = db.query(MonthlySalaryReport).filter(MonthlySalaryReport.report_id == report_id).first()
    if db_salary_report:
        db.delete(db_salary_report)
        db.commit()
        return True
    return False