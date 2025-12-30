from enum import Enum
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Float
from sqlalchemy.sql.schema import ForeignKey
from database.database import Base
import enum

class GradeEnum(str, enum.Enum):
    大一 = '大一'
    大二 = '大二'
    大三 = '大三'
    大四 = '大四'
    已毕业 = '已毕业'

class UserProfile(Base):
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True, comment='用户ID（与登录表id完全一致）')
    username = Column(String(50), ForeignKey('user_login.username', ondelete='CASCADE'), nullable=False, unique=True, comment='用户名（与登录表一致）')
    avatar = Column(String(500), comment='头像文件路径/URL')
    grade = Column(SQLEnum(GradeEnum), comment='年级')
    postgraduate_session = Column(String(20), comment='考研届数（如2026届）')
    school = Column(String(100), comment='就读学校')
    major = Column(String(100), comment='就读专业')
    target_school = Column(String(100), comment='预期考研学校')
    target_major = Column(String(100), comment='预期考研专业')
    target_score = Column(Float, comment='预期考研分数')

    __table_args__ = {
        'comment': '学习助手-考研个人信息表',
        'extend_existing': True
    }