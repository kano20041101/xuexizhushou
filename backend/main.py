import sys
import os
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import Optional, List
import uuid
from datetime import datetime
from sqlalchemy import text
from pydantic import BaseModel
from database.database import get_db, engine, Base
from models.user_login import UserLogin
from models.user_profile import UserProfile, GradeEnum
from models.knowledge_point import KnowledgePoint
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

# ==================== 知识点管理 API ====================

class KnowledgePointCreate(BaseModel):
    id: int
    subject: str
    point_name: str
    category: str
    importance: str = "中"
    difficulty: str = "中"
    exam_points: Optional[str] = None
    content: Optional[str] = None

class KnowledgePointUpdate(BaseModel):
    subject: Optional[str] = None
    point_name: Optional[str] = None
    category: Optional[str] = None
    importance: Optional[str] = None
    difficulty: Optional[str] = None
    exam_points: Optional[str] = None
    content: Optional[str] = None

# 获取用户的所有知识点
@app.get("/knowledge-points/{user_id}")
def get_knowledge_points(user_id: int, subject: Optional[str] = None, db: Session = Depends(get_db)):
    # 验证用户是否存在
    user = db.query(UserLogin).filter(UserLogin.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 查询知识点
    query = db.query(KnowledgePoint).filter(KnowledgePoint.id == user_id)
    if subject:
        query = query.filter(KnowledgePoint.subject == subject)
    
    knowledge_points = query.order_by(KnowledgePoint.create_time.desc()).all()
    
    # 转换为字典列表
    result = []
    for kp in knowledge_points:
        result.append({
            "kp_id": kp.kp_id,
            "id": kp.id,
            "subject": kp.subject,
            "point_name": kp.point_name,
            "category": kp.category,
            "importance": kp.importance,
            "difficulty": kp.difficulty,
            "exam_points": kp.exam_points,
            "content": kp.content,
            "create_time": kp.create_time.isoformat() if kp.create_time else None,
            "update_time": kp.update_time.isoformat() if kp.update_time else None
        })
    
    return result

# 创建知识点
@app.post("/knowledge-points")
def create_knowledge_point(kp: KnowledgePointCreate, db: Session = Depends(get_db)):
    # 验证用户是否存在
    user = db.query(UserLogin).filter(UserLogin.id == kp.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查知识点是否已存在
    existing_kp = db.query(KnowledgePoint).filter(
        KnowledgePoint.id == kp.id,
        KnowledgePoint.point_name == kp.point_name
    ).first()
    
    if existing_kp:
        raise HTTPException(status_code=400, detail="该知识点已存在")
    
    # 创建新知识点
    new_kp = KnowledgePoint(
        id=kp.id,
        subject=kp.subject,
        point_name=kp.point_name,
        category=kp.category,
        importance=kp.importance,
        difficulty=kp.difficulty,
        exam_points=kp.exam_points,
        content=kp.content,
        create_time=datetime.now(),
        update_time=datetime.now()
    )
    
    db.add(new_kp)
    db.commit()
    db.refresh(new_kp)
    
    return {
        "message": "知识点创建成功",
        "kp_id": new_kp.kp_id
    }

# 更新知识点
@app.put("/knowledge-points/{kp_id}")
def update_knowledge_point(kp_id: int, kp_update: KnowledgePointUpdate, db: Session = Depends(get_db)):
    # 查找知识点
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.kp_id == kp_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    
    # 更新字段
    if kp_update.subject is not None:
        kp.subject = kp_update.subject
    if kp_update.point_name is not None:
        kp.point_name = kp_update.point_name
    if kp_update.category is not None:
        kp.category = kp_update.category
    if kp_update.importance is not None:
        kp.importance = kp_update.importance
    if kp_update.difficulty is not None:
        kp.difficulty = kp_update.difficulty
    if kp_update.exam_points is not None:
        kp.exam_points = kp_update.exam_points
    if kp_update.content is not None:
        kp.content = kp_update.content
    
    kp.update_time = datetime.now()
    
    db.commit()
    db.refresh(kp)
    
    return {"message": "知识点更新成功"}

# 删除知识点
@app.delete("/knowledge-points/{kp_id}")
def delete_knowledge_point(kp_id: int, db: Session = Depends(get_db)):
    # 查找知识点
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.kp_id == kp_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    
    db.delete(kp)
    db.commit()
    
    return {"message": "知识点删除成功"}

# 获取单个知识点详情
@app.get("/knowledge-points/detail/{kp_id}")
def get_knowledge_point_detail(kp_id: int, db: Session = Depends(get_db)):
    kp = db.query(KnowledgePoint).filter(KnowledgePoint.kp_id == kp_id).first()
    if not kp:
        raise HTTPException(status_code=404, detail="知识点不存在")
    
    return {
        "kp_id": kp.kp_id,
        "id": kp.id,
        "subject": kp.subject,
        "point_name": kp.point_name,
        "category": kp.category,
        "importance": kp.importance,
        "difficulty": kp.difficulty,
        "exam_points": kp.exam_points,
        "content": kp.content,
        "create_time": kp.create_time.isoformat() if kp.create_time else None,
        "update_time": kp.update_time.isoformat() if kp.update_time else None
    }