from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.monthly_salary_report import MonthlySalaryReport, MonthlySalaryReportCreate, MonthlySalaryReportUpdate
from app.crud import monthly_salary_report as crud
from reportlab.pdfgen import canvas
from fastapi.responses import StreamingResponse
import io
import pandas as pd

router = APIRouter(prefix="/monthly-salary-reports", tags=["monthly-salary-reports"])

@router.post("/", response_model=MonthlySalaryReport)
def create_salary_report(salary_report: MonthlySalaryReportCreate, db: Session = Depends(get_db)):
    return crud.create_salary_report(db=db, salary_report=salary_report)

@router.get("/", response_model=list[MonthlySalaryReport])
def read_salary_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    salary_reports = crud.get_salary_reports(db, skip=skip, limit=limit)
    return salary_reports

@router.get("/month/{month_year}", response_model=list[MonthlySalaryReport])
def read_salary_reports_by_month(month_year: str, db: Session = Depends(get_db)):
    salary_reports = crud.get_salary_reports_by_month(db, month_year=month_year)
    return salary_reports

@router.get("/{report_id}", response_model=MonthlySalaryReport)
def read_salary_report(report_id: int, db: Session = Depends(get_db)):
    db_salary_report = crud.get_salary_report(db, report_id=report_id)
    if db_salary_report is None:
        raise HTTPException(status_code=404, detail="Salary report not found")
    return db_salary_report

@router.put("/{report_id}", response_model=MonthlySalaryReport)
def update_salary_report(report_id: int, salary_report: MonthlySalaryReportUpdate, db: Session = Depends(get_db)):
    db_salary_report = crud.update_salary_report(db, report_id=report_id, salary_report=salary_report)
    if db_salary_report is None:
        raise HTTPException(status_code=404, detail="Salary report not found")
    return db_salary_report

@router.delete("/{report_id}")
def delete_salary_report(report_id: int, db: Session = Depends(get_db)):
    success = crud.delete_salary_report(db, report_id=report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Salary report not found")
    return {"message": "Salary report deleted successfully"}

@router.get("/export-pdf")
def export_salary_pdf(month_year: str, db: Session = Depends(get_db)):
    salary_reports = crud.get_salary_reports_by_month(db, month_year=month_year)
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    
    # Add PDF content
    p.drawString(100, 800, f"Salary Report - {month_year}")
    y = 780
    for report in salary_reports:
        p.drawString(100, y, f"{report.name}: {report.net_salary}")
        y -= 20
    
    p.save()
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="application/pdf", 
                           headers={"Content-Disposition": f"attachment; filename=salary_report_{month_year}.pdf"})
@router.get("/export-excel")
def export_salary_excel(month_year: str, db: Session = Depends(get_db)):
    salary_reports = crud.get_salary_reports_by_month(db, month_year=month_year)
    
    # Convert to DataFrame
    data = []
    for report in salary_reports:
        data.append({
            'Name': report.name,
            'Captain ID': report.careem_captain_id,
            'Net Salary': report.net_salary,
            # Add other fields
        })
    
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Salary Report', index=False)
    
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           headers={"Content-Disposition": f"attachment; filename=salary_report_{month_year}.xlsx"})
