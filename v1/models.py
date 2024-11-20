from pydantic import BaseModel,Field
from datetime import datetime
from enum import Enum
from typing import Optional, List

class UserRole(str, Enum):
    Admin = "Admin"
    User = "User"
    Subscriber = "Subscriber"

class Gender(str, Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"

class User(BaseModel):
    id: int
    username: str
    email: str
    picture: Optional[str]
    role: UserRole
    createdAt: datetime
    profession: Optional[str] = None
    interest: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[Gender] = None
    city: Optional[str] = None
    country: Optional[str] = None

    translations: List['Translation'] = []
    speechToTexts: List['SpeechToTexts'] = []
    textToSpeechs: List['TextToSpeech'] = []
    ocrs: List['OCR'] = []

    threads: List['Thread'] = []
    chats: List['Chat'] = []

    likedTranslations: List['Translation'] = []
    likedSpeechToTexts: List['SpeechToTexts'] = []
    likedTextToSpeechs: List['TextToSpeech'] = []
    likedOcrs: List['OCR'] = []
    likedChats: List['Chat'] = []
    

class Translation(BaseModel):
    id: str
    input: str
    output: str
    inputLang: str
    outputLang: str
    responseTime: str
    ipAddress: str
    version: Optional[str]
    sourceApp: Optional[str]
    createdAt: datetime
    city: Optional[str]
    country: Optional[str]
    editOutput: Optional[str]

    userId: Optional[int]
    user: Optional[User]
    likedByUsers: List[User] = []

class SpeechToTexts(BaseModel):
    id: str
    input: str
    output: str
    responseTime: str
    ipAddress: str
    version: Optional[str]
    sourceApp: Optional[str]
    createdAt: datetime
    city: Optional[str]
    country: Optional[str]
    editOutput: Optional[str]

    userId: Optional[int]
    user: Optional[User]
    likedByUsers: List[User] = []

class TextToSpeech(BaseModel):
    id: str
    input: str
    output: str
    responseTime: str
    ipAddress: str
    version: Optional[str]
    sourceApp: Optional[str]
    createdAt: datetime
    city: Optional[str]
    country: Optional[str]

    userId: Optional[int]
    user: Optional[User]
    likedByUsers: List[User] = []

class OCR(BaseModel):
    id: str
    input: str
    output: str
    responseTime: str
    ipAddress: str
    version: Optional[str]
    sourceApp: Optional[str]
    createdAt: datetime
    city: Optional[str]
    country: Optional[str]
    editOutput: Optional[str]

    userId: Optional[int]
    user: Optional[User]
    likedByUsers: List[User] = []

class Thread(BaseModel):
    id: str
    title: str
    createdById: int
    createdBy: User
    createdAt: datetime
    updatedAt: datetime
    is_completed:bool
    show:bool
    # Relationships
    chats: List['Chat'] = []

class Chat(BaseModel):
    id: str
    content: str
    threadId: int
    thread: Thread
    senderId: int
    sender: User
    createdAt: datetime
    updatedAt: datetime
    likedByUsers: List[User] = []
    latency: int = Field(..., description="Latency in milliseconds")
    token: int = Field(..., description="Token count or identifier")


# Resolve forward references
User.update_forward_refs()
Translation.update_forward_refs()
SpeechToTexts.update_forward_refs()
TextToSpeech.update_forward_refs()
OCR.update_forward_refs()
Thread.update_forward_refs()
Chat.update_forward_refs()