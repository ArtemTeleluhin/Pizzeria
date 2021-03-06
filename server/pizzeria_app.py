from server.data import db_session
from server.data.categories import Categories
from server.data.dishes import Dishes
from server.data.versions import Versions
from server.data.orders import Orders
from server.data.versions_to_orders import VersionsToOrders
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QWidget, QLabel, QListWidgetItem, QVBoxLayout, QAction, QListWidgetItem, QStatusBar
from server.widgets import OrdersListWidget, CategoriesTable, DishesTable, VersionsTable
from PyQt5 import QtCore

DB_NAME = 'pizzeria_base'
BOTTOM_PADDING = 30
UPDATE_FREQUENCY = 15 * 1000


class AppWindow(QMainWindow):
    def __init__(self, db_sess):
        super().__init__()
        self.setWindowTitle('Приложение пиццерии')
        self.db_sess = db_sess

        self.ordersInProgress = OrdersListWidget(self.db_sess, only_not_completed=True)
        self.setCentralWidget(self.ordersInProgress)

        self.to_orders_in_progress = QAction(self)
        self.to_orders_in_progress.setText('Текущие заказы')
        self.menuBar().addAction(self.to_orders_in_progress)
        self.to_orders_in_progress.triggered.connect(self.show_orders_in_progress)

        self.to_recent_orders = QAction(self)
        self.to_recent_orders.setText('Недавние заказы')
        self.menuBar().addAction(self.to_recent_orders)
        self.to_recent_orders.triggered.connect(self.show_recent_orders)

        self.to_categories_table = QAction(self)
        self.to_categories_table.setText('Категории')
        self.menuBar().addAction(self.to_categories_table)
        self.to_categories_table.triggered.connect(self.show_categories_table)

        self.to_dishes_table = QAction(self)
        self.to_dishes_table.setText('Блюда')
        self.menuBar().addAction(self.to_dishes_table)
        self.to_dishes_table.triggered.connect(self.show_dishes_table)

        self.to_versions_table = QAction(self)
        self.to_versions_table.setText('Версии блюд')
        self.menuBar().addAction(self.to_versions_table)
        self.to_versions_table.triggered.connect(self.show_versions_table)

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.setFixedSize(
            self.ordersInProgress.size().width(),
            self.ordersInProgress.size().height() + BOTTOM_PADDING
        )

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(UPDATE_FREQUENCY)
        self.timer.timeout.connect(self.update_orders_list)
        self.timer.start()

    def show_orders_in_progress(self):
        self.ordersInProgress = OrdersListWidget(self.db_sess, only_not_completed=True)
        self.setCentralWidget(self.ordersInProgress)

    def show_recent_orders(self):
        self.recentOrders = OrdersListWidget(self.db_sess, only_recent=True)
        self.setCentralWidget(self.recentOrders)

    def show_categories_table(self):
        self.categoriesTable = CategoriesTable(self.db_sess, self.message)
        self.setCentralWidget(self.categoriesTable)

    def show_dishes_table(self):
        self.dishesTable = DishesTable(self.db_sess, self.message)
        self.setCentralWidget(self.dishesTable)

    def show_versions_table(self):
        self.versionsTable = VersionsTable(self.db_sess, self.message)
        self.setCentralWidget(self.versionsTable)

    @QtCore.pyqtSlot()
    def update_orders_list(self):
        if isinstance(self.centralWidget(), OrdersListWidget):
            self.centralWidget().update_list()

    def message(self, text):
        self.statusbar.showMessage(text)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    db_session.global_init(f'db/{DB_NAME}.db')
    db_sess = db_session.create_session()

    app = QApplication(sys.argv)
    ex = AppWindow(db_sess)
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
