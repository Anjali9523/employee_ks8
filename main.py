from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from kubernetes import client, config
import os

DATABASE_URL = "sqlite:////tmp/employees.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class EmployeeDB(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

class Employee(BaseModel):
    id: int
    name: str
    role: str

    class Config:
        orm_mode = True

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_employee_cr(emp: Employee):
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()

    crd_api = client.CustomObjectsApi()
    GROUP = "mydomain.com"
    VERSION = "v1"
    PLURAL = "employeeapis"
    NAMESPACE = os.environ.get("EMPLOYEE_NAMESPACE", "employee")

    body = {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "EmployeeAPI",
        "metadata": {"name": emp.name},
        "spec": emp.dict()
    }

    try:
        crd_api.create_namespaced_custom_object(
            group=GROUP,
            version=VERSION,
            namespace=NAMESPACE,
            plural=PLURAL,
            body=body
        )
        print(f"Successfully created EmployeeApi CR for {emp.name}")
    except client.rest.ApiException as e:
        print(f"Error creating custom resource: {e.status} {e.reason} {e.body}")
        if e.status != 409:
            raise

@app.post("/employee/", response_model=Employee)
def create_employee(emp: Employee, db: Session = Depends(get_db)):
    db_emp = db.query(EmployeeDB).filter(EmployeeDB.id == emp.id).first()
    if db_emp:
        raise HTTPException(status_code=400, detail="Employee already exists")
    new_emp = EmployeeDB(id=emp.id, name=emp.name, role=emp.role)
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    # Create the Kubernetes CR
    print("About to call create_employee_cr")
    create_employee_cr(emp)
    return new_emp

@app.get("/employee/{emp_id}", response_model=Employee)
def get_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(EmployeeDB).filter(EmployeeDB.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

@app.get("/employees/", response_model=List[Employee])
def list_employees(db: Session = Depends(get_db)):
    return db.query(EmployeeDB).all()
