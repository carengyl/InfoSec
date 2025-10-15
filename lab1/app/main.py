from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base, User, Post
from security import get_password_hash, create_access_token, sanitize_html
from auth import authenticate_user, get_current_user
from pydantic import BaseModel

app = FastAPI()

Base.metadata.create_all(bind=engine)


class UserLogin(BaseModel):
    username: str
    password: str


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: str

    class Config:
        from_attributes = True


def create_test_user(db: Session):
    if not db.query(User).filter(User.username == "testuser").first():
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("testpassword")
        )
        db.add(user)
        db.commit()
        print("Test user created: testuser / testpassword")


@app.on_event("startup")
def on_startup():
    db = next(get_db())
    create_test_user(db)
    db.close()


@app.post("/auth/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/data")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    sanitized_posts = []
    for post in posts:
        sanitized_posts.append(PostResponse(
            id=post.id,
            title=sanitize_html(post.title),
            content=sanitize_html(post.content),
            author_id=post.author_id,
            created_at=post.created_at.isoformat()
        ))
    return sanitized_posts


@app.post("/api/data")
def create_post(post_data: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sanitized_title = sanitize_html(post_data.title)
    sanitized_content = sanitize_html(post_data.content)

    db_post = Post(
        title=sanitized_title,
        content=sanitized_content,
        author_id=current_user.id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return PostResponse(
        id=db_post.id,
        title=db_post.title,
        content=db_post.content,
        author_id=db_post.author_id,
        created_at=db_post.created_at.isoformat()
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)