from sqlalchemy import String, Text, ForeignKey, BigInteger
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Banner(Base):
    __tablename__ = 'banner'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), unique=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)
    phone: Mapped[str] = mapped_column(String(13), nullable=True)


class Service(Base):
    __tablename__ = 'services'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    image: Mapped[str] = mapped_column(String(150), nullable=True)


class Dentist(Base):
    __tablename__ = 'dentists'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200))
    education: Mapped[str] = mapped_column(String(200))
    medical_category: Mapped[str] = mapped_column(String(30))
    professional_skills: Mapped[str] = mapped_column(String(400))
    image: Mapped[str] = mapped_column(String(150), nullable=True)
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id'))

    service: Mapped['Service'] = relationship(backref='dentists')


class Reserve(Base):
    __tablename__ = 'reservations'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String(12), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))
    dentist_id: Mapped[int] = mapped_column(ForeignKey('dentists.id'))
