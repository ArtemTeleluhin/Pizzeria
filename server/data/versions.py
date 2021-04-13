import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Versions(SqlAlchemyBase):
    __tablename__ = 'versions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    size = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    dish_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("dishes.id"))
    dish = orm.relation('Dishes')
    con_orders = orm.relation("VersionsToOrders", back_populates='version')
