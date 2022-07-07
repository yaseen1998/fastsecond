import os

from pathlib import Path

class Settings:
    PROJECT_NAME:str = "Job Board"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER : str = 'dewtdhaz'
    POSTGRES_PASSWORD = '0dvyd1pqfFiGTdALMeiMtzplDoz7TDdz'
    POSTGRES_SERVER : str = 'jelani.db.elephantsql.com'
    POSTGRES_PORT : str = '5432' # default postgres port is 5432
    POSTGRES_DB : str = 'dewtdhaz'
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

settings = Settings()