from fastapi import FastAPI
from app.routes import limo_payments
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables

from app.routes import (
    dashboard,
    employees, 
    partners, 
    wps_vendors, 
    weekly_trips, 
    deductions, 
    monthly_salary_reports,
    auto_salary
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(employees.router)
app.include_router(partners.router)
app.include_router(wps_vendors.router)
app.include_router(weekly_trips.router)
app.include_router(deductions.router)
app.include_router(monthly_salary_reports.router)
app.include_router(auto_salary.router)
app.include_router(limo_payments.router)

@app.on_event("startup")
def on_startup():
    create_tables()

@app.get("/")
def read_root():
    return {"message": "Rider Salary Management System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)