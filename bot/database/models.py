from sqlalchemy import Column, Integer, String, BigInteger, Text, Float, DateTime, ForeignKey, Enum as PgEnum
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class QuestionStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    ANSWERED = "answered"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    role = Column(PgEnum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    questions = relationship("Question", back_populates="user")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(PgEnum(QuestionStatus), default=QuestionStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="questions")
    payment = relationship("Payment", back_populates="question", uselist=False)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), unique=True)
    amount = Column(Float, nullable=False)
    proof_file_id = Column(String, nullable=False)
    status = Column(PgEnum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    question = relationship("Question", back_populates="payment")
