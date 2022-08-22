from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy import Boolean, Column, Float, String, Integer

app = FastAPI()

# SqlAlchemy Setup
SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///places.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#define the tables for User and todos
class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    fname = Column(String)
    lname = Column(String)
    email = Column(String,unique=True,index=True)
    todos = relationship("TODO",back_populates="owner",cascade="all, delete-orphan")

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    completed = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="todos")

#Define a pedantic class - it is a schema  for the signup process
#create user

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    fname: str
    lname: str
    password: str

class TODOcreate(BaseModel):
    text: str
    completed: bool

class TODOupdate(TODOcreate):
    id: int


#fuctions
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def add_user(db: Session, user_data: UserCreate) -> UserCreate:
    db_user = User(
        email=user_data.email,
        fname=user_data.fname,
        lname=user_data.lname,
        password=user_data.password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/users",response_model=User)
def sign_up(user_data: UserCreate, db: Session = Depends(get_db)):
    user = get_user_by_email(db, UserCreate.email)
    if user:
        raise HTTPException(
            status_code=409,
            detail="This email has already been registered."
        )
    else:
        new_user = add_user(db,user_data)
        return new_user


