import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Dishes(SqlAlchemyBase):
    __tablename__ = 'dishes'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    add_info = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    category_id = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("categories.id"))
    category = orm.relation('Categories')
    versions = orm.relation("Versions", back_populates='dish')
    is_sale = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
