from pathlib import Path
from sqlalchemy import create_engine,event
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from app.config import settings
if settings.DATABASE_URL.startswith('sqlite:///'):
    Path(settings.DATABASE_URL.replace('sqlite:///','',1)).parent.mkdir(parents=True,exist_ok=True)
    args={'check_same_thread':False}
else: args={}
engine=create_engine(settings.DATABASE_URL,connect_args=args,pool_pre_ping=True)
if settings.DATABASE_URL.startswith('sqlite'):
    @event.listens_for(engine,'connect')
    def fk_on(conn,record):
        cur=conn.cursor();cur.execute('PRAGMA foreign_keys=ON');cur.close()
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
class Base(DeclarativeBase): pass
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
