from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    last_name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    mail = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    expert = Column(Boolean, default=False)
    score = Column(Integer, default=0)
    
    # Relationships - ЯВНО указываем foreign_keys
    ideas = relationship("Idea", back_populates="author_rel", foreign_keys="Idea.author_id")
    moderated_ideas = relationship("Idea", back_populates="moderator_rel", foreign_keys="Idea.moderator_id")
    comments = relationship("Comment", back_populates="user_rel")
    achievements = relationship("UserAchievement", back_populates="user_rel")
    products = relationship("UserProduct", back_populates="user_rel")

class Achievement(Base):
    __tablename__ = "achievement"
    
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    title = Column(Text, unique=True, nullable=False)
    image_file = Column(String, nullable=False)
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement_rel")

class UserAchievement(Base):
    __tablename__ = "user_achievement"
    
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievement.id"), nullable=False)
    
    # Relationships
    user_rel = relationship("User", back_populates="achievements")
    achievement_rel = relationship("Achievement", back_populates="user_achievements")

class Status(Base):
    __tablename__ = "status"
    
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    title = Column(Text, unique=True, nullable=False)
    
    # Relationships
    ideas = relationship("Idea", back_populates="status_rel")

class Idea(Base):
    __tablename__ = "idea"
    
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("status.id"), nullable=False)
    moderator_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - ЯВНО указываем foreign_keys
    author_rel = relationship("User", back_populates="ideas", foreign_keys=[author_id])
    moderator_rel = relationship("User", back_populates="moderated_ideas", foreign_keys=[moderator_id])
    status_rel = relationship("Status", back_populates="ideas")
    comments = relationship("Comment", back_populates="idea_rel")

class Comment(Base):
    __tablename__ = "comment"
    
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    content = Column(String, nullable=False)
    datetime = Column(DateTime, default=datetime.utcnow)
    idea_id = Column(Integer, ForeignKey("idea.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # Relationships
    idea_rel = relationship("Idea", back_populates="comments")
    user_rel = relationship("User", back_populates="comments")

class Product(Base):
    __tablename__ = "product"
    
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    image = Column(String, nullable=False)
    
    # Relationships
    user_products = relationship("UserProduct", back_populates="product_rel")

class UserProduct(Base):
    __tablename__ = "user_product"
    
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    
    # Relationships
    user_rel = relationship("User", back_populates="products")
    product_rel = relationship("Product", back_populates="user_products")