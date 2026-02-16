from sqlalchemy import Column, Integer, String, BigInteger, Text, Float, DateTime, ForeignKey, Enum as PgEnum, Boolean
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
    role = Column(PgEnum(UserRole, values_callable=lambda x: [e.value for e in x]), default=UserRole.USER)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    questions = relationship("Question", back_populates="user")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(PgEnum(QuestionStatus, values_callable=lambda x: [e.value for e in x]), default=QuestionStatus.PENDING)
    
    # AI Classification fields
    complexity = Column(String, nullable=True)  # 'simple', 'medium', 'complex'
    ai_confidence = Column(Float, nullable=True)  # 0.0 - 1.0
    category = Column(String, nullable=True)  # 'mehnat', 'fuqarolik', etc.
    auto_answered = Column(Boolean, default=False)  # AI gave free answer
    requires_human = Column(Boolean, default=False)  # Needs lawyer
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="questions")
    payment = relationship("Payment", back_populates="question", uselist=False)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), unique=True)
    amount = Column(Float, nullable=False)
    proof_file_id = Column(String, nullable=True)  # Optional for online payments
    payment_method = Column(String, default="manual")  # 'manual', 'click', 'payme'
    invoice_id = Column(String, nullable=True)  # Online payment invoice ID
    payment_url = Column(String, nullable=True)  # Payment link for online
    status = Column(PgEnum(PaymentStatus, values_callable=lambda x: [e.value for e in x]), default=PaymentStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    question = relationship("Question", back_populates="payment")
