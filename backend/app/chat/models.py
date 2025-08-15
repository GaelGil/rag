from sqlalchemy.types import UserDefinedType


from app.extensions import db


# Define pgvector type
class Vector(UserDefinedType):
    def get_col_spec(self):
        return "vector(1536)"  # change depending on vector dimension size


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    embedding = db.Column(Vector)  # pgvector column
