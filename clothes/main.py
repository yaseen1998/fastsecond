from datetime import datetime,timedelta
from typing import Optional
import databases
import enum
import jwt
import sqlalchemy
from pydantic import BaseModel, validator
from fastapi import Depends, FastAPI
from decouple import config
from email_validator import validate_email as validate_e
from passlib.context import CryptContext
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from starlette.requests import Request

DATABASE_URL = "sqlite:///./clothes.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

class UserRole(enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    user = "user"

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
    sqlalchemy.Column("role", sqlalchemy.Enum(UserRole), nullable=False, server_default=UserRole.user.name),
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

class CustomHttpBearer(HTTPBearer):
    async def __call__(
        self, request: Request
        ) -> Optional[HTTPAuthorizationCredentials]:
        
        res = await super().__call__(request)
        try:
            payload = jwt.decode(res.credentials, config("SECRET_KEY"), algorithms=["HS256"])
            user = await database.fetch_one( users.select().where(users.c.id == payload["sub"]))
            request.state.user = user
            print(request.state.user['email'])
            return payload
        except Exception as e:
            raise e
    

oauth2_scheme = CustomHttpBearer()    

def create_access_token(user):
    try :
        payload = {'sub':user['id'],'exp':datetime.utcnow() + timedelta(minutes=60)}
        return jwt.encode(payload, 'b6995d25-11ef-40d0-89f3-1c7de1a3a3af', algorithm='HS256')
    except Exception as e:
        raise e
    
    
@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    
    
@app.get("/clothes/",dependencies=[Depends(oauth2_scheme)])
async def get_all_clothes():
    return await database.fetch_all(clothes.select())
    
@app.post("/register/",) # remove  response_model=UserSignOut when call token 
async def create_user(user:UserSignIn):
    user.password = pwd_context.hash(user.password)
    q = users.insert().values(**user.dict())
    id_ = await database.execute(q)
    user = await database.fetch_one(users.select().where(users.c.id == id_))
    token = create_access_token(user)
    
    return {"token":token}
    
    
