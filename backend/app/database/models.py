from sqlalchemy import Column,Integer,String,DateTime,ForeignKey,UniqueConstraint,Boolean
from sqlalchemy.orm import relationship,declarative_base
from datetime import datetime,timezone


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String(100),unique=True,nullable=False,index=True)
    password_hash = Column(String(255),nullable=False)
    created_at = Column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),nullable=False)
    conversations = relationship("Conversation",back_populates="user",cascade="all, delete-orphan")
    documents = relationship("Document",back_populates="user",cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken",back_populates="user",cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    user = relationship("User", back_populates="refresh_tokens")
    
class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True)
    title = Column(String(255),nullable=False)
    created_at = Column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),nullable=False)
    user = relationship("User",back_populates="conversations")
    messages = relationship("Message",back_populates="conversation",cascade="all, delete-orphan")
    documents = relationship("ConversationDocument",back_populates="conversation",cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer,primary_key=True,index=True)
    conversation_id = Column(Integer,ForeignKey("conversations.id",ondelete="CASCADE"),nullable=False,index=True)
    role = Column(String,nullable=False)
    content = Column(String,nullable=False)
    created_at = Column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),nullable=False)
    conversation = relationship("Conversation",back_populates="messages")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True)
    filename = Column(String,nullable=False)
    # file_path = Column(String,nullable=False)
    s3_key = Column(String,nullable=False)
    file_hash = Column(String(64),nullable=False)
    created_at = Column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),nullable=False)
    user = relationship("User",back_populates="documents")
    conversations = relationship("ConversationDocument",back_populates="document",cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "file_hash",
            name = "uq_user_document_hash"
        ),
    )

class ConversationDocument(Base):
    __tablename__ = "conversation_documents"
    id = Column(Integer,primary_key=True,index=True)
    conversation_id = Column(Integer,ForeignKey("conversations.id",ondelete="CASCADE"),nullable=False,index=True)
    document_id = Column(Integer,ForeignKey("documents.id",ondelete="CASCADE"),nullable=False,index=True)
    created_at = Column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),nullable=False)
    conversation = relationship("Conversation",back_populates="documents")
    document = relationship("Document",back_populates="conversations")

