from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from .database.database import get_db, engine, Base
from backend.models.user_login import UserLogin
from sqlalchemy import func

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

class UserCreate(BaseModel):
    username: str
    password: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"message": "数据库连接成功", "status": "healthy"}
    except Exception as e:
        return {"message": f"数据库连接失败: {str(e)}", "status": "error"}

@app.get("/user-login/")
def read_user_login(db: Session = Depends(get_db)):
    users = db.query(UserLogin).all()
    return users

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserLogin).filter(UserLogin.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = UserLogin(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}

@app.post("/login")
def login(user: UserLoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(UserLogin).filter(func.lower(UserLogin.username) == func.lower(user.username)).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="用户名不存在")
    elif db_user.password != user.password:
        raise HTTPException(status_code=401, detail="密码错误")
    return {"message": "Login successful", "user_id": db_user.id}