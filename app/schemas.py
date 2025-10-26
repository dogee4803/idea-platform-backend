from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# User Schemas
class UserBase(BaseModel):
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    mail: EmailStr
    expert: bool = False
    score: int = 0

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    mail: EmailStr
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

# Achievement Schemas
class AchievementBase(BaseModel):
    title: str
    image_file: str

class Achievement(AchievementBase):
    id: int
    
    class Config:
        from_attributes = True

class UserAchievementBase(BaseModel):
    user_id: int
    achievement_id: int

class UserAchievement(UserAchievementBase):
    id: int
    
    class Config:
        from_attributes = True

# Status Schemas
class StatusBase(BaseModel):
    title: str

class Status(StatusBase):
    id: int
    
    class Config:
        from_attributes = True

# Idea Schemas
class IdeaBase(BaseModel):
    title: str
    description: str
    status_id: int = 1  # default status

class IdeaCreate(IdeaBase):
    pass

class Idea(IdeaBase):
    id: int
    author_id: int
    moderator_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Comment Schemas
class CommentBase(BaseModel):
    content: str
    idea_id: int

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    user_id: int
    datetime: datetime
    
    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    title: str
    description: str
    price: int
    quantity: int
    image: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    
    class Config:
        from_attributes = True

class UserProductBase(BaseModel):
    user_id: int
    product_id: int

class UserProduct(UserProductBase):
    id: int
    
    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None