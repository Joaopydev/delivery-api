#uvicorn main:app --reload
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/signin")

from src.routes.auth_routes import auth_router
from src.routes.order_routes import order_router

app.include_router(order_router)
app.include_router(auth_router)
