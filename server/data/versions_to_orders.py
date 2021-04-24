import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class VersionsToOrders(SqlAlchemyBase):
    __tablename__ = 'versions_to_orders'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    order_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("orders.id"))
    order = orm.relation('Orders')
    version_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("versions.id"))
    version = orm.relation('Versions')
    count = sqlalchemy.Column(sqlalchemy.Integer)
