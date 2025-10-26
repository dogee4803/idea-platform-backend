from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
import os

from . import crud, models, schemas
from .database import create_tables, get_db
from .auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

# Create tables
create_tables()

app = FastAPI(title="Idea Platform API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем папки для статических файлов если их нет
os.makedirs("app/static/achievements", exist_ok=True)
os.makedirs("app/static/products", exist_ok=True)

# Настраиваем обслуживание статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Auth endpoints
@app.post("/auth/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.mail)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return crud.create_user(db=db, user=user)

@app.post("/auth/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    authenticated_user = crud.authenticate_user(db, user.mail, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": authenticated_user.mail}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Idea endpoints
@app.get("/ideas/", response_model=List[schemas.Idea])
def read_ideas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ideas = crud.get_ideas(db, skip=skip, limit=limit)
    return ideas

@app.post("/ideas/", response_model=schemas.Idea)
def create_idea(
    idea: schemas.IdeaCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_idea(db=db, idea=idea, user_id=current_user.id)

@app.get("/users/me/ideas", response_model=List[schemas.Idea])
def read_user_ideas(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_user_ideas(db, user_id=current_user.id)

# Comment endpoints
@app.get("/ideas/{idea_id}/comments", response_model=List[schemas.Comment])
def read_idea_comments(idea_id: int, db: Session = Depends(get_db)):
    return crud.get_idea_comments(db, idea_id=idea_id)

@app.post("/comments/", response_model=schemas.Comment)
def create_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_comment(db=db, comment=comment, user_id=current_user.id)

# Achievement endpoints - возвращаем с полными URL
@app.get("/achievements/")
def read_achievements(request: Request, db: Session = Depends(get_db)):
    achievements = crud.get_achievements(db)
    
    # Преобразуем в dict с полными URL
    result = []
    for achievement in achievements:
        achievement_dict = {
            "id": achievement.id,
            "title": achievement.title,
            "image_url": f"{request.base_url}static/achievements/{achievement.image_file}"
        }
        result.append(achievement_dict)
    
    return result

@app.get("/users/me/achievements")
def read_user_achievements(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_achievements = crud.get_user_achievements(db, user_id=current_user.id)
    
    result = []
    for ua in user_achievements:
        achievement_dict = {
            "id": ua.achievement_rel.id,
            "title": ua.achievement_rel.title,
            "image_url": f"{request.base_url}static/achievements/{ua.achievement_rel.image_file}"
        }
        result.append(achievement_dict)
    
    return result

# Product endpoints - возвращаем с полными URL
@app.get("/products/")
def read_products(request: Request, db: Session = Depends(get_db)):
    products = crud.get_products(db)
    
    result = []
    for product in products:
        product_dict = {
            "id": product.id,
            "title": product.title,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity,
            "image_url": f"{request.base_url}static/products/{product.image}"
        }
        result.append(product_dict)
    
    return result

@app.post("/products/buy", response_model=schemas.UserProduct)
def buy_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    user_product = schemas.UserProductBase(user_id=current_user.id, product_id=product_id)
    result = crud.buy_product(db, user_product)
    if not result:
        raise HTTPException(status_code=400, detail="Product not available")
    return result

@app.get("/")
def read_root():
    return {"message": "Idea Platform API is running"}


# Score endpoints
@app.get("/users/me/score")
def get_my_score(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return {"user_id": current_user.id, "score": current_user.score}

@app.post("/users/me/score/add")
def add_my_score(
    points: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_score = crud.add_user_score(db, current_user.id, points)
    if new_score is not None:
        return {"user_id": current_user.id, "new_score": new_score, "message": f"Added {points} points"}
    raise HTTPException(status_code=400, detail="Failed to add points")

@app.post("/users/me/score/subtract")
def subtract_my_score(
    points: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_score = crud.subtract_user_score(db, current_user.id, points)
    if new_score is not None:
        return {"user_id": current_user.id, "new_score": new_score, "message": f"Subtracted {points} points"}
    raise HTTPException(status_code=400, detail="Failed to subtract points")

# Admin endpoints for score management (только для экспертов/админов)
@app.post("/users/{user_id}/score")
def set_user_score_admin(
    user_id: int,
    new_score: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Проверяем что текущий пользователь эксперт
    if not current_user.expert:
        raise HTTPException(status_code=403, detail="Only experts can modify user scores")
    
    result = crud.set_user_score(db, user_id, new_score)
    if result is not None:
        return {"user_id": user_id, "new_score": result, "message": "Score updated"}
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/scores")
def get_all_scores(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Только эксперты могут видеть все счета
    if not current_user.expert:
        raise HTTPException(status_code=403, detail="Only experts can view all scores")
    
    users = db.query(models.User).all()
    return [{"user_id": user.id, "name": f"{user.first_name} {user.last_name}", "score": user.score} for user in users]