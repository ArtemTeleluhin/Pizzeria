import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
import datetime


class Orders(SqlAlchemyBase):
    __tablename__ = 'orders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    customer_name = sqlalchemy.Column(sqlalchemy.String)
    telephone_number = sqlalchemy.Column(sqlalchemy.String)
    address = sqlalchemy.Column(sqlalchemy.String)
    sum_price = sqlalchemy.Column(sqlalchemy.Integer)
    time = sqlalchemy.Column(sqlalchemy.DateTime,
                             default=datetime.datetime.now)
    is_done = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    con_versions = orm.relation("VersionsToOrders", back_populates='order')
