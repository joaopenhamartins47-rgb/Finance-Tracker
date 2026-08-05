
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.exceptions import AppException
from models import Base
from database import engine
from routers import auth, user, account
app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(account.router)