from sqlalchemy import Boolean,Column,ForeignKey,Integer,String,DateTime,Enum
from sqlalchemy.sql import func
from db import Base
import enum

class UserRole(enum.Enum):
    Admin = "Admin"
    User = "User"
    Subscriber = "Subscriber"


class Users(Base):
    __tablename__ = 'users'
    
    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    username=Column(String)
    email=Column(String)
    picture=Column(String,nullable=True)
    role = Column(Enum(UserRole), nullable=False,default='User')
    created_at = Column(DateTime, default=func.now()) 
    
    def __repr__(self):
        return f"<User(email='{self.email}', username='{self.username}')>"

    def __str__(self):
        return f"User {self.username} ({self.email})"
    
class Translations(Base):
    __tablename__ = 'translations'
    
    id = Column(Integer,primary_key=True, index=True,autoincrement=True)
    input=Column(String)
    output=Column(String)
    input_lang=Column(String)
    output_lang=Column(String)
    response_time=Column(String)
    ip_address=Column(String)
    version=Column(String,nullable=True)
    source_app=Column(String,nullable=True)
    created_at = Column(DateTime, default=func.now()) 
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
class SpeechToTexts(Base):
    __tablename__ = 'speech_to_texts'
    
    id = Column(Integer,primary_key=True, index=True,autoincrement=True)
    input=Column(String)
    output=Column(String)
    response_time=Column(String)
    ip_address=Column(String)
    version=Column(String,nullable=True)
    source_app=Column(String,nullable=True)
    created_at = Column(DateTime, default=func.now()) 
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
class TextToSpeech(Base):
    __tablename__ = 'text_to_speechs'
    
    id = Column(Integer,primary_key=True, index=True,autoincrement=True)
    input=Column(String)
    output=Column(String)
    response_time=Column(String)
    ip_address=Column(String)
    version=Column(String,nullable=True)
    source_app=Column(String,nullable=True)
    created_at = Column(DateTime, default=func.now()) 
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
class OCR(Base):
    __tablename__ = 'ocrs'
    
    id = Column(Integer,primary_key=True, index=True,autoincrement=True)
    input=Column(String)
    output=Column(String)
    response_time=Column(String)
    ip_address=Column(String)
    version=Column(String,nullable=True)
    source_app=Column(String,nullable=True)
    created_at = Column(DateTime, default=func.now()) 
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    