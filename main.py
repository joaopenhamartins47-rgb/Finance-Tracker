
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from core.exceptions import AppException
from models import Base
from database import engine
from routers import auth
app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )

app.include_router(auth.router)