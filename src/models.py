from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
import enum


db = SQLAlchemy()

class Climates(enum.Enum):
    DESERT = 1
    ICY = 2
    JUNGLE = 3
    VOLCANIC = 4
    ACUATIC = 5

class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorites: Mapped[List["Favorite"]] = relationship(back_populates = "user")
    
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    
class Character(db.Model):
    __tablename__ = 'character'
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(250), nullable = False)
    description: Mapped[str] = mapped_column(String(500), nullable = True)
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="character")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }
    
class Planet(db.Model):
    __tablename__ = 'planet'
    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(250), nullable = False)
    climate: Mapped[Climates] = mapped_column(Enum(Climates), nullable = True)
    population: Mapped[int] = mapped_column(nullable = True)
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="planet")

    def serializ(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population
        }
    
class Favorite(db.Model):
    __tablename__ = 'favorites'
    id: Mapped[int] = mapped_column(primary_key = True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable = False)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"), nullable = True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable = True)

    user: Mapped["User"] = relationship(back_populates="favorites")
    character: Mapped["Character"] = relationship(back_populates="favorites")
    planet: Mapped["Planet"] = relationship(back_populates="favorites")

    def serialize(self):    
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id
        }

