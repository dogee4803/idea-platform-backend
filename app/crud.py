from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User CRUD
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.mail == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        last_name=user.last_name,
        first_name=user.first_name,
        middle_name=user.middle_name,
        mail=user.mail,
        password=hashed_password,
        expert=user.expert
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user

# Idea CRUD
def get_ideas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Idea).offset(skip).limit(limit).all()

def get_user_ideas(db: Session, user_id: int):
    return db.query(models.Idea).filter(models.Idea.author_id == user_id).all()

def create_idea(db: Session, idea: schemas.IdeaCreate, user_id: int):
    db_idea = models.Idea(**idea.dict(), author_id=user_id)
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea

def update_idea_status(db: Session, idea_id: int, status_id: int, moderator_id: int = None):
    db_idea = db.query(models.Idea).filter(models.Idea.id == idea_id).first()
    if db_idea:
        db_idea.status_id = status_id
        if moderator_id:
            db_idea.moderator_id = moderator_id
        db.commit()
        db.refresh(db_idea)
    return db_idea

# Comment CRUD
def get_idea_comments(db: Session, idea_id: int):
    return db.query(models.Comment).filter(models.Comment.idea_id == idea_id).all()

def create_comment(db: Session, comment: schemas.CommentCreate, user_id: int):
    db_comment = models.Comment(**comment.dict(), user_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

# Achievement CRUD
def get_achievements(db: Session):
    return db.query(models.Achievement).all()

def get_user_achievements(db: Session, user_id: int):
    return db.query(models.UserAchievement).filter(models.UserAchievement.user_id == user_id).all()

def add_user_achievement(db: Session, user_achievement: schemas.UserAchievementBase):
    db_achievement = models.UserAchievement(**user_achievement.dict())
    db.add(db_achievement)
    db.commit()
    db.refresh(db_achievement)
    return db_achievement

# Product CRUD
def get_products(db: Session):
    return db.query(models.Product).all()

def get_user_products(db: Session, user_id: int):
    return db.query(models.UserProduct).filter(models.UserProduct.user_id == user_id).all()

def buy_product(db: Session, user_product: schemas.UserProductBase):
    # Check if product exists and has quantity
    product = db.query(models.Product).filter(models.Product.id == user_product.product_id).first()
    if not product or product.quantity <= 0:
        return None
    
    user = db.query(models.User).filter(models.User.id == user_product.user_id).first()
    if not user or user.score < product.price:
        return None  # Недостаточно очков
    
    spend_points_for_product(db, user_product.user_id, product.price)
    
    # Decrease product quantity
    product.quantity -= 1
    
    # Create user product relationship
    db_user_product = models.UserProduct(**user_product.dict())
    db.add(db_user_product)
    db.commit()
    db.refresh(db_user_product)
    return db_user_product

# Score CRUD operations
def get_user_score(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user.score if user else 0

def add_user_score(db: Session, user_id: int, points: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.score += points
        db.commit()
        db.refresh(user)
        return user.score
    return None

def subtract_user_score(db: Session, user_id: int, points: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        # Не позволяем уйти в минус
        user.score = max(0, user.score - points)
        db.commit()
        db.refresh(user)
        return user.score
    return None

def set_user_score(db: Session, user_id: int, new_score: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.score = max(0, new_score)  # Не позволяем уйти в минус
        db.commit()
        db.refresh(user)
        return user.score
    return None

def spend_points_for_product(db: Session, user_id: int, product_price: int):
    """Списать очки за покупку товара"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user and user.score >= product_price:
        return subtract_user_score(db, user_id, product_price)
    return None