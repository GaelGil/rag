from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import UserDefinedType

Base = declarative_base()


# Define pgvector type
class Vector(UserDefinedType):
    def get_col_spec(self):
        return "vector(1536)"  # change depending on vector dimension size


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    embedding = Column(Vector)  # pgvector column
