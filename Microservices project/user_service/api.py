# user_service/api.py
from fastapi import FastAPI
from pydantic import BaseModel
from service import UserService

app = FastAPI()

class UserCreate(BaseModel):
    email: str
    password: str

@app.post("/users")
def create_user(user: UserCreate):
    return UserService.create_user(user.dict())
