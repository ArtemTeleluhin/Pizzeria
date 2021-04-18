from server.data import db_session
from server.data.categories import Categories
from server.data.dishes import Dishes
from server.data.versions import Versions
from server.data.orders import Orders
from server.data.versions_to_orders import VersionsToOrders
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QWidget, QLabel, QListWidgetItem, QVBoxLayout, QPlainTextEdit, QListWidgetItem
from server.UI.orders_list import Ui_Form as Ui_orders_list
from server.UI.order_info import Ui_MainWindow as Ui_order_info
from datetime import datetime, timedelta


class OrderWidget(QMainWindow, Ui_order_info):
    def __init__(self, db_sess, order):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Заказ')
        self.setFixedSize(self.size())

        self.db_sess = db_sess
        self.order = order

        self.outputAddress.setText(order.address)
        if order.customer_name:
            if order.telephone_number:
                self.outputInfo.setText(f'{order.customer_name}, {order.telephone_number}')
            else:
                self.outputInfo.setText(order.customer_name)
        elif order.telephone_number:
            self.outputInfo.setText(f'{order.telephone_number}')
        self.outputSum.setText(str(order.sum_price))
        self.outputTime.setText(order.time.strftime('%d.%m.%Y %H:%M'))

        self.outputAddress.setEnabled(False)
        self.outputInfo.setEnabled(False)
        self.outputSum.setEnabled(False)
        self.outputTime.setEnabled(False)

        for con in order.con_versions:
            version = con.version
            version_text = f'{version.dish.name}, {version.size}, {int(version.price)}'
            self.orderList.addItem(QListWidgetItem(version_text))

        if order.is_done:
            self.pushButton.setEnabled(False)
            self.statusbar.showMessage('Заказ уже выполнен')
        else:
            self.pushButton.clicked.connect(self.order_completed)

    def order_completed(self):
        self.order.is_done = True
        self.db_sess.commit()
        self.close()


class OrdersListItem(QListWidgetItem):
    def __init__(self, text, order_id):
        super().__init__(text)
        self.order_id = order_id

    def take_order_id(self):
        return self.order_id


class OrdersListWidget(QWidget, Ui_orders_list):
    def __init__(self, db_sess, only_recent=False, only_not_completed=False):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())

        self.db_sess = db_sess
        self.only_recent = only_recent
        self.only_not_completed = only_not_completed
        self.old_orders_id = None
        self.opened_windows = []

        self.update_list()
        self.pushButton.clicked.connect(self.show_order)

    def update_list(self):
        if self.only_not_completed:
            orders = self.db_sess.query(Orders).filter(Orders.is_done == 0)
        else:
            orders = self.db_sess.query(Orders).all()
        if self.only_recent:
            today = datetime.now().date()
            orders = filter(lambda obj: (obj.time.date() == today or
                                         obj.time.date() == today - timedelta(days=1)), orders)
        orders = list(orders)
        orders.sort(key=lambda obj: obj.time)
        orders.reverse()
        new_orders_id = frozenset(obj.id for obj in orders)
        if self.old_orders_id != new_orders_id:
            self.ordersList.clear()
            for order in orders:
                item_text = order.time.strftime('%d.%m.%Y %H:%M') + ', ' + order.address
                self.ordersList.addItem(OrdersListItem(item_text, order.id))
            self.old_orders_id = new_orders_id

    def show_order(self):
        current_item = self.ordersList.currentItem()
        if current_item:
            order_id = current_item.take_order_id()
            order = self.db_sess.query(Orders).filter(Orders.id == order_id).first()
            if order:
                new_window = OrderWidget(self.db_sess, order)
                self.opened_windows.append(new_window)
                new_window.show()
