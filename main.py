#uvicorn main:app --reload
import logging
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from src.events_listeners.order_listeners import * # to register the event listeners

# Set up logging to see SQL statements
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.orm").setLevel(logging.INFO)
logging.getLogger("sqlalchemy").setLevel(logging.ERROR)

app = FastAPI()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/signin")

from src.routes.auth_routes import auth_router
from src.routes.order_routes import order_router

app.include_router(order_router)
app.include_router(auth_router)
