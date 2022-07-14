from datetime import datetime
from typing import Optional
import databases
import enum
import sqlalchemy
from pydantic import BaseModel, validator
from fastapi import FastAPI
from decouple import config
from email_validator import validate_email as validate_e
from passlib.context import CryptContext

DATABASE_URL = "sqlite:///./clothes.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(120), unique=True),
    sqlalchemy.Column("password", sqlalchemy.String(255)),
    sqlalchemy.Column("full_name", sqlalchemy.String(200)),
    sqlalchemy.Column("phone", sqlalchemy.String(13)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)


class ColorEnum(enum.Enum):
    pink = "pink"
    black = "black"
    white = "white"
    yellow = "yellow"


class SizeEnum(enum.Enum):
    xs = "xs"
    s = "s"
    m = "m"
    l = "l"
    xl = "xl"
    xxl = "xxl"

clothes = sqlalchemy.Table(
    "clothes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(120)),
    sqlalchemy.Column("color", sqlalchemy.Enum(ColorEnum), nullable=False),
    sqlalchemy.Column("size", sqlalchemy.Enum(SizeEnum), nullable=False),
    sqlalchemy.Column("photo_url", sqlalchemy.String(255)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)
class EmailField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, value)->str:
        if not validate_e(value):
            raise ValueError("Invalid email")
        return value
        # try :
        #     validate_e(value)
        #     return value
        # except Exception as e:
        #     raise ValueError("Invalid email")
        


class BaseUser(BaseModel):
    email:EmailField
    full_name:str
    
    # @validator('email')
    # def validate_email(cls,v):
    #     try :
    #         validate_e(v)
    #         return v
    #     except Exception as e:
    #         raise ValueError("Invalid email")
        
    @validator('full_name')
    def validate_full_name(cls,v):
        try :
            first_name, last_name = v.split(" ")
            return v
        except Exception as e:
            raise ValueError("Invalid full name")
    
    
class UserSignIn(BaseUser):
    password:str
    

class UserSignOut(BaseUser):
    phonr:Optional[str]
    created_at:datetime
    last_modified_at:datetime
    
    
app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    
    
@app.post("/register/", response_model=UserSignOut)
async def create_user(user:UserSignIn):
    user.password = pwd_context.hash(user.password)
    q = users.insert().values(**user.dict())
    id_ = await database.execute(q)
    user = await database.fetch_one(users.select().where(users.c.id == id_))
    return user
    
    
