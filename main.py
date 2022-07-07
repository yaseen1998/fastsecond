import databases
from fastapi import FastAPI,Request
import sqlalchemy
from decouple import config
print(config('DB_USER'))

DATABASE_URL = "sqlite:///./test.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


books = sqlalchemy.Table('books', 
                         metadata,
                         sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                         sqlalchemy.Column('title',sqlalchemy.String),
                         sqlalchemy.Column('author',sqlalchemy.String),
                         sqlalchemy.Column('pages',sqlalchemy.Integer),
                         sqlalchemy.Column('word ',sqlalchemy.Integer),
                        #  sqlalchemy.Column('reader_id',sqlalchemy.ForeignKey('readers.id'),nullable=True,index=True),
                        )

readers = sqlalchemy.Table('readers',
                           metadata,
                           sqlalchemy.Column('id',sqlalchemy.Integer,primary_key=True),
                           sqlalchemy.Column('first_name',sqlalchemy.String),
                           sqlalchemy.Column('last_name',sqlalchemy.String),
                           )

readers_books = sqlalchemy.Table('readers_books',
                                 metadata,
                           sqlalchemy.Column('id',sqlalchemy.Integer,primary_key=True),
                           sqlalchemy.Column('book_id',sqlalchemy.ForeignKey('books.id'),nullable=True,index=True),
                           sqlalchemy.Column('reader_id',sqlalchemy.ForeignKey('readers.id'),nullable=True,index=True),
                           )

# engine = sqlalchemy.create_engine(DATABASE_URL,connect_args={"check_same_thread": False})
# metadata.create_all(engine) 

 
app = FastAPI()

@app.on_event('startup')
async def startup():
    await database.connect()
    
@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
    
    
@app.get('/books/')
async def get_all_books():
    query = books.select()
    return await database.fetch_all(query)



@app.post('/books/')
async def create_book(request: Request):
    data = await request.json()
    query = books.insert().values(**data)
    last_record_id = await database.execute(query)
    return {'id': last_record_id}

@app.post('/readers/')
async def create_reader(request: Request):
    data = await request.json()
    query = readers.insert().values(**data)
    last_record_id = await database.execute(query)
    return {'id': last_record_id}

@app.post('/read/')
async def create_read(request: Request):
    data = await request.json()
    query = readers_books.insert().values(**data)
    last_record_id = await database.execute(query)
    return {'id': last_record_id}

