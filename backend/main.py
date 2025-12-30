from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import Optional, List
import os
import uuid
from datetime import datetime
from sqlalchemy import text
from pydantic import BaseModel
from database.database import get_db, engine, Base
from models.user_login import UserLogin
from models.user_profile import UserProfile, GradeEnum
from sqlalchemy import func
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
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

# 配置头像上传目录
AVATAR_UPLOAD_DIR = "uploads/avatars"
os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)

@app.get("/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    # 查找用户是否存在
    user = db.query(UserLogin).filter(UserLogin.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取用户资料
    profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not profile:
        # 如果用户资料不存在，创建一个新的
        profile = UserProfile(id=user_id, username=user.username)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # 转换为字典并返回
    profile_dict = {
        "id": profile.id,
        "username": profile.username,
        "avatar": f"/{profile.avatar}" if profile.avatar else None,
        "grade": profile.grade.value if profile.grade else None,
        "postgraduate_session": profile.postgraduate_session,
        "school": profile.school,
        "major": profile.major,
        "target_school": profile.target_school,
        "target_major": profile.target_major,
        "target_score": profile.target_score
    }
    return profile_dict

@app.put("/profile/{user_id}")
def update_profile(
    user_id: int,
    grade: Optional[str] = Form(None),
    postgraduate_session: Optional[str] = Form(None),
    school: Optional[str] = Form(None),
    major: Optional[str] = Form(None),
    target_school: Optional[str] = Form(None),
    target_major: Optional[str] = Form(None),
    target_score: Optional[float] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # 查找用户是否存在
    user = db.query(UserLogin).filter(UserLogin.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取用户资料
    profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not profile:
        profile = UserProfile(id=user_id, username=user.username)
        db.add(profile)

    # 更新基本信息
    if grade:
        try:
            profile.grade = GradeEnum(grade)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的年级值")
    if postgraduate_session:
        profile.postgraduate_session = postgraduate_session
    if school:
        profile.school = school
    if major:
        profile.major = major
    if target_school:
        profile.target_school = target_school
    if target_major:
        profile.target_major = target_major
    if target_score:
        profile.target_score = target_score

    # 处理头像上传
    if avatar:
        # 生成唯一文件名
        file_ext = os.path.splitext(avatar.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(AVATAR_UPLOAD_DIR, filename)

        # 保存文件
        with open(file_path, "wb") as f:
            f.write(avatar.file.read())

        # 更新头像路径
        profile.avatar = file_path

    # 提交更改
    db.commit()
    db.refresh(profile)

    return {"message": "个人信息更新成功"}