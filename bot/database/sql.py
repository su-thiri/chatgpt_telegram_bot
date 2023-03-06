from typing import Optional, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy import types
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime
import json
import uuid
import zlib

import config

Base = declarative_base()

class GzipString(types.TypeDecorator):

    impl = types.LargeBinary

    cache_ok = True

    def process_bind_param(self, value: str, dialect):
        if value is not None:
            return zlib.compress(value.encode())
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return zlib.decompress(value).decode()
        return None

# define User class
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    last_interaction = Column(DateTime, default=datetime.datetime.utcnow)
    first_seen = Column(DateTime, default=datetime.datetime.utcnow)
    current_dialog_id = Column(String, ForeignKey("dialogs.id"))
    current_chat_mode = Column(String)
    n_used_tokens = Column(Float)

    # define relationship with Dialog class
    current_dialog = relationship("Dialog", foreign_keys=[current_dialog_id])

    def __repr__(self):
        return f"<User(chat_id={self.chat_id}, username={self.username}, current_chat_mode={self.current_chat_mode}, current_dialog_id={self.current_dialog_id})>"

# define Dialog class
class Dialog(Base):
    __tablename__ = "dialogs"
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_mode = Column(String)
    messages = Column(GzipString)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Dialog(user_id={self.user_id}, chat_mode={self.chat_mode}, start_time={self.start_time})>"
    

_session = None

def sessionFactory():
    global _session
    
    if _session is not None:
        return _session
    
    # create database engine
    engine = create_engine(config.sql_uri, echo=False)

    Base.metadata.create_all(engine)

    # session maker
    _session = sessionmaker(bind=engine)

    return _session

class Database:
    def __init__(self):
        try:
            self.session = sessionFactory()
        except Exception as e:
            print(e)
            raise e

    def check_if_user_exists(self, user_id: int, raise_exception: bool = False):
        with self.session() as session:

            exists = session.query(User).filter_by(id=user_id).count() > 0

            if exists:
                return True
            else:
                if raise_exception:
                    raise ValueError(f"User {user_id} does not exist")
                else:
                    return False
            
    def add_new_user(
        self,
        user_id: int,
        chat_id: int,
        username: str = "",
        first_name: str = "",
        last_name: str = "",
    ):

        if not self.check_if_user_exists(user_id):
            user = User(id=user_id, chat_id=chat_id, username=username, first_name=first_name, last_name=last_name, current_chat_mode="assistant", n_used_tokens=0)
            with self.session() as session:
                session.add(user)
                session.commit()

    def start_new_dialog(self, user_id: int):
        self.check_if_user_exists(user_id, raise_exception=True)

        dialog_id = str(uuid.uuid4())
        dialog = Dialog(id=dialog_id, user_id=user_id, chat_mode=self.get_user_attribute(user_id, "current_chat_mode"))

        with self.session() as session:
            # add new dialog
            session.add(dialog)
            # update user's current dialog
            session.query(User).filter_by(id=user_id).update({User.current_dialog_id: dialog_id})
            session.commit()

    def get_user_attribute(self, user_id: int, key: str):
        with self.session() as session:
            user = session.query(User).filter_by(id=user_id).one()
            
            if not hasattr(user, key):
                raise ValueError(f"User {user_id} does not have a value for {key}")
            
            return getattr(user, key)

    def set_user_attribute(self, user_id: int, key: str, value: Any):
        with self.session() as session:
            user = session.query(User).filter_by(id=user_id).one()
            setattr(user, key, value)

    def get_dialog_messages(self, user_id: int, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        with self.session() as session:
            dialog = session.query(Dialog).filter_by(id=dialog_id, user_id=user_id).one()
            messages = json.loads(dialog.messages) if dialog.messages else []
            
            for m in messages:
                m['date'] = datetime.datetime.strptime(m['date'], '%Y-%m-%d %H:%M:%S.%f')
            
            return messages
    
    def set_dialog_messages(self, user_id: int, dialog_messages: list, dialog_id: Optional[str] = None):
        self.check_if_user_exists(user_id, raise_exception=True)

        if dialog_id is None:
            dialog_id = self.get_user_attribute(user_id, "current_dialog_id")

        json_string = json.dumps(dialog_messages, default=str) if dialog_messages else None
        
        with self.session() as session:
            session.query(Dialog).filter_by(id=dialog_id, user_id=user_id).update({Dialog.messages: json_string})
            session.commit()
