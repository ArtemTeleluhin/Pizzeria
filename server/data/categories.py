import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Categories(SqlAlchemyBase):
    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    dishes = orm.relation("Dishes", back_populates='category')
