import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    registration_id = Column(String(100), nullable=True)
    gmail_token = Column(Text, nullable=True)  # JSON-encoded OAuth token
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    shortlist_results = relationship("ShortlistResult", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"


class ShortlistResult(Base):
    __tablename__ = "shortlist_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company = Column(String(255), nullable=True)
    exam_date = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False)  # selected, not_selected, error
    checked_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="shortlist_results")

    def __repr__(self):
        return f"<ShortlistResult user={self.user_id} status={self.status}>"
