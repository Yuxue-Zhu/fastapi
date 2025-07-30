from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.future import select
from datetime import datetime

from model import Base, User, Log
from database import engine, get_session
from sqlalchemy.ext.asyncio import AsyncSession


app = FastAPI()

class LoginRequest(BaseModel):
    email: str
    password: str

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/login")
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user.last_login = datetime.now()
    user.login_count += 1
    session.add(user)

    session.add(Log(user_id=user.id))
    await session.commit()

    return {"message": "Login successful"}
