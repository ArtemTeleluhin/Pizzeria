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


class OrderWidget(QMainWindow, Ui_order_info):
    def __init__(self, db_sess, order):
        super().__init__()
        self.setupUi(self)
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
