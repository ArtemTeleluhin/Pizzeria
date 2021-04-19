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
from server.UI.db_table import Ui_Form as Ui_db_table
from server.UI.category_dialog import Ui_MainWindow as Ui_category_dialog
from server.UI.dish_dialog import Ui_MainWindow as Ui_dish_dialog
from server.UI.version_dialog import Ui_MainWindow as Ui_version_dialog
from datetime import datetime, timedelta

MAX_PRICE = 10 ** 6


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


class CategoryDialog(QMainWindow, Ui_category_dialog):
    def __init__(self, parent, db_sess, category_id=None):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())

        self.parent = parent
        self.db_sess = db_sess
        self.category_id = category_id
        if category_id is None:
            self.category = None
        else:
            self.category = self.db_sess.query(Categories).filter(Categories.id == category_id)
            self.inputName.setText(self.category.name)
        self.saveButton.clicked.connect(self.save)

    def save(self):
        name = self.inputName.text()
        if not name:
            self.message('Имя категории не может быть пустым')
            return
        alternative_category = self.db_sess.query(Categories).filter(
            Categories.name == name,
            Categories.id != self.category_id
        ).first()
        if alternative_category:
            self.message('Уже есть другая категория с таким названием')
            return
        if self.category:
            self.category.name = name
        else:
            self.category = Categories(name=name)
            self.db_sess.add(self.category)
        self.db_sess.commit()
        self.parent.update_table()
        self.close()

    def message(self, text):
        self.statusbar.showMessage(text)


class DishDialog(QMainWindow, Ui_dish_dialog):
    def __init__(self, parent, db_sess, dish_id=None):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())

        self.parent = parent
        self.db_sess = db_sess
        self.dish_id = dish_id

        for category in self.db_sess.query(Categories).all():
            self.chooseCategory.addItem(category.name)

        if dish_id:
            self.dish = self.db_sess.query(Dishes).filter(Dishes.id == dish_id)
            self.chooseCategory.setCurrentText(self.dish.category.name)
            self.inputName.setText(self.dish.name)
            self.inputAddInfo.setText(self.dish.add_info)
            self.checkIsSale.setChecked(self.dish.is_sale)
        else:
            self.dish = None
        self.saveButton.clicked.connect(self.save)

    def save(self):
        category_name = self.chooseCategory.currentText()
        name = self.inputName
        add_info = self.inputAddInfo
        is_sale = self.checkIsSale.isChecked()
        if not name:
            self.message('Имя блюда не может быть пустым')
            return
        alternative_dish = self.db_sess.query(Dishes).filter(
            Dishes.name == name,
            Dishes.id != self.dish_id
        ).first()
        if alternative_dish:
            self.message('Уже есть другое блюдо с таким названием')
            return
        category = self.db_sess.query(Categories).filter(Categories.name == category_name).first()
        if self.dish:
            self.dish.category = category
            self.dish.name = name
            self.dish.add_info = add_info
            self.dish.is_sale = is_sale
        else:
            self.dish = Dishes(category=category, name=name, add_info=add_info, is_sale=is_sale)
            self.db_sess.add(self.dish)
        self.db_sess.commit()
        self.parent.update_table()
        self.close()

    def message(self, text):
        self.statusbar.showMessage(text)


class VersionDialog(QMainWindow, Ui_version_dialog):
    def __init__(self, parent, db_sess, version_id=None):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.size())

        self.parent = parent
        self.db_sess = db_sess
        self.version_id = version_id

        self.inputPrice.setMaximum(MAX_PRICE)
        for category in self.db_sess.query(Categories).all():
            self.chooseCategory.addItem(category.name)

        if version_id:
            self.version = self.db_sess.query(Versions).filter(Versions.id == version_id).first()
            self.chooseCategory.setCurrentText(self.version.dish.category.name)
            self.update_choose_dish()
            self.chooseDish.setCurrentText(self.version.dish.name)
            self.inputSize.setText(self.version.size)
            self.inputPrice.setValue(self.version.price)
        else:
            self.version = None
            self.update_choose_dish()
        self.chooseCategory.currentIndexChanged.connect(self.update_choose_dish)
        self.saveButton.clicked.connect(self.save)

    def update_choose_dish(self):
        category_name = self.chooseCategory.currentText()
        category = self.db_sess.query(Categories).filter(Categories.name == category_name).first()
        self.chooseDish.clear()
        for dish in self.db_sess.query(Dishes).filter(Dishes.category == category):
            self.chooseDish.addItem(dish.name)

    def save(self):
        dish_name = self.chooseDish.currentText()
        size = self.inputSize.text()
        price = self.inputPrice.value()
        dish = self.db_sess.query(Dishes).filter(Dishes.name == dish_name).first()
        if not size:
            self.message('Размер блюда не может быть пустым')
            return
        alternative_version = self.db_sess.query(Versions).filter(
            Versions.size == size,
            Versions.dish == dish,
            Versions.id != self.version_id
        ).first()
        if alternative_version:
            self.message('Уже есть такой размер блюда')
            return
        if self.version:
            self.version.dish = dish
            self.version.size = size
            self.version.price = price
        else:
            self.version = Versions(dish=dish, size=size, price=price)
            self.db_sess.add(self.version)
        self.db_sess.commit()
        self.parent.update_table()
        self.close()

    def message(self, text):
        self.statusbar.showMessage(text)
