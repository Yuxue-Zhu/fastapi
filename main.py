from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import delete
from sqlalchemy.future import select
from datetime import datetime

from model import Base, LoginRequest, User, Log
from database import AsyncSessionLocal, engine, get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # initialize user data when starting up
    async with AsyncSessionLocal() as session:
    
        users = [
                User(email=f"user{i}@example.com", password=f"123456test{i}")
                for i in range(1000)
            ]
        session.add_all(users)
        await session.commit()

    yield
    # clean up when shutting down
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

app = FastAPI(lifespan=lifespan)

@app.post("/login")
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user.last_login = datetime.now()
    user.login_count += 1

    session.add(Log(user_id=user.id))
    await session.commit()
    await session.refresh(user)

    return {"message": "Login successful"}
