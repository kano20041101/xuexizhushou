from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.orm import relationship
from database.database import Base
import enum

class ImportanceEnum(str, enum.Enum):
    低 = '低'
    中 = '中'
    高 = '高'
    必考 = '必考'

class DifficultyEnum(str, enum.Enum):
    易 = '易'
    较易 = '较易'
    中 = '中'
    较难 = '较难'
    难 = '难'

class KnowledgePoint(Base):
    __tablename__ = 'knowledge_point'

    kp_id = Column(Integer, primary_key=True, autoincrement=True, comment='知识点序号（自增，知识点唯一标识）')
    id = Column(Integer, ForeignKey('user_login.id', ondelete='CASCADE'), nullable=False, comment='用户ID（关联user_login.id，归属哪个用户的知识点）')
    subject = Column(String(50), nullable=False, comment='科目（如：数据结构、计算机组成原理、操作系统、计算机网络）')
    point_name = Column(String(100), nullable=False, comment='知识点名称（如：二叉树遍历）')
    category = Column(String(50), nullable=False, comment='分类')
    importance = Column(String(20), nullable=False, default='中', comment='重要度（低/中/高/必考）')
    difficulty = Column(String(20), nullable=False, default='中', comment='难度（易/较易/中/较难/难）')
    exam_points = Column(String(200), nullable=True, comment='考点（如：选择题、计算题、论述题）')
    content = Column(Text, nullable=True, comment='知识点详细内容')
    create_time = Column(DateTime, nullable=False, comment='创建时间')
    update_time = Column(DateTime, nullable=False, comment='更新时间')

    # 关系
    user = relationship("UserLogin", backref="knowledge_points")

    __table_args__ = (
        Index('idx_id_subject', 'id', 'subject'),
        UniqueConstraint('id', 'point_name', name='idx_id_pointname'),
        {'comment': '学习助手-考研知识点管理表（id=用户ID，kp_id=知识点序号）'}
    )
