import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtWidgets import QMainWindow, QLabel, QSpinBox

import requests
from flask import Flask, jsonify, request
from pprint import pprint

from requests import post
from customer_interface.product import Product

PIZZERIA_ADDRESS = input().rstrip()  # "http://127.0.0.1:8080"
NUMBER_OF_CURRENT_NOTES = 6
START_TEXT = 'Всё'


class Order:
    def __init__(self, name, telephone, address, list_of_products, sum_price):
        self.name = name
        self.telephone = telephone
        self.address = address
        self.list_of_products = list_of_products
        self.sum_price = sum_price
        self.json_formatted = {}

    def get_json(self):
        self.json_formatted['order'] = []
        for product_info in self.list_of_products:
            product = product_info[0]
            proportion = product_info[1]
            ind_of_proportion = product_info[2]
            tmp = {
                'name': product.get_name(),
                'size': proportion['size'],
                'price': proportion['price'],
                'count': product.take_number_of_proportion(ind_of_proportion)
            }
            self.json_formatted['order'].append(tmp)
        if '' not in [self.sum_price, self.name, self.telephone, self.address]:
            self.json_formatted['sum_price'] = self.sum_price
            self.json_formatted['name'] = self.name
            self.json_formatted['telephone_number'] = self.telephone
            self.json_formatted['address'] = self.address
        return self.json_formatted

    def send_order(self):
        return post(f'{PIZZERIA_ADDRESS}/make_order', json=self.get_json()).json()


class CollectOrder(QMainWindow):
    def __init__(self, menu):
        super().__init__()
        self.counts = []
        self.counts_to_proportion = {}
        self.labels = []
        self.current = 0
        self.menu = menu
        self.start('Всё')
        self.setFixedSize(self.size())

    def start(self, text, new_type=True):
        if new_type:
            self.current = 0
        uic.loadUi('choose_products.ui', self)
        unique_types = set()
        self.comboBox.addItem(text)
        unique_types.add(text)
        unique_types.add(START_TEXT)
        for type_of_product in self.menu.keys():
            for product in self.menu[type_of_product]:
                unique_types.add(product.get_type())
        for unique_type in unique_types:
            if unique_type == text:
                continue
            self.comboBox.addItem(unique_type)
        self.labels.clear()
        self.counts.clear()
        self.initUI()
        self.comboBox.currentTextChanged.connect(self.start)

    def new_lbl(self, name):
        self.labels.append(QLabel(self))
        self.labels[-1].setText(name)

    def new_val(self, val):
        self.counts_to_proportion[self.sender()][0].set_proportion(self.counts_to_proportion[self.sender()][1], val)

    def new_cnt(self, product, j):
        self.counts.append(QSpinBox(self))
        self.counts_to_proportion[self.counts[-1]] = [product, j]
        self.counts[-1].setValue(int(product.take_number_of_proportion(j)))
        self.counts[-1].valueChanged.connect(self.new_val)

    def open_basket(self):
        self.second_form = Basket(self.menu)
        self.setCentralWidget(self.second_form)

    def forward_notes(self):
        if self.current + NUMBER_OF_CURRENT_NOTES <= len(self.menu[self.comboBox.currentText()]):
            self.current += NUMBER_OF_CURRENT_NOTES
            self.start(self.comboBox.currentText(), False)

    def back_notes(self):
        if self.current - NUMBER_OF_CURRENT_NOTES >= 0:
            self.current -= NUMBER_OF_CURRENT_NOTES
            self.start(self.comboBox.currentText(), False)

    def initUI(self):
        self.Basket.clicked.connect(self.open_basket)
        self.forward.clicked.connect(self.forward_notes)
        self.back.clicked.connect(self.back_notes)
        for i, product in enumerate(
                self.menu[self.comboBox.currentText()][
                self.current:min(self.current + NUMBER_OF_CURRENT_NOTES, len(self.menu[self.comboBox.currentText()]))]):
            self.new_lbl(product.get_name())
            self.gridLayout_3.addWidget(self.labels[-1], i, 0)
            for j, proportion in enumerate(product.get_proportion()):
                self.new_lbl(f"{proportion['size']}\n{str(proportion['price'])}руб.")
                self.gridLayout_3.addWidget(self.labels[-1], i, 2 * j + 2)
                self.new_cnt(product, j)
                self.gridLayout_3.addWidget(self.counts[-1], i, 2 * j + 1)
        self.setFixedSize(self.size())


class Basket(QMainWindow):
    def __init__(self, menu):
        super().__init__()
        uic.loadUi('basket.ui', self)
        self.labels = []
        self.menu = menu
        self.last_row = 0
        self.cost = 0
        self.current = 0
        self.order_products = []
        for i, product in enumerate(self.menu[START_TEXT]):
                for j, proportion in enumerate(product.get_proportion()):
                    if product.take_number_of_proportion(j) != 0:
                        self.cost += product.take_number_of_proportion(j) * proportion['price']
                        self.order_products.append([product, proportion, j])
        self.buttons_connect()
        self.show_chosen_menu()
        self.setFixedSize(self.size())

    def new_lbl(self, name):
        self.labels.append(QLabel(self))
        self.labels[-1].setText(name)

    def forward_notes(self):
        if self.current + NUMBER_OF_CURRENT_NOTES <= len(self.order_products):
            self.current += NUMBER_OF_CURRENT_NOTES
            self.show_chosen_menu()

    def back_notes(self):
        if self.current - NUMBER_OF_CURRENT_NOTES >= 0:
            self.current -= NUMBER_OF_CURRENT_NOTES
            self.show_chosen_menu()

    def show_row(self, product, proportion, id_proportion):
        self.new_lbl(product.get_name())
        self.gridLayout.addWidget(self.labels[-1], self.last_row, 0)
        self.new_lbl(f" * {str(product.take_number_of_proportion(id_proportion))}")
        self.gridLayout.addWidget(self.labels[-1], self.last_row, 2)
        self.new_lbl(f"{proportion['size']}\n{str(proportion['price'])}руб.")
        self.gridLayout.addWidget(self.labels[-1], self.last_row, 1)
        self.last_row += 1

    def to_collect_order(self):
        self.collect_order = CollectOrder(self.menu)
        self.setCentralWidget(self.collect_order)

    def show_chosen_menu(self):
        uic.loadUi('basket.ui', self)
        self.buttons_connect()
        for product_info in self.order_products[
                            self.current:min(self.current + NUMBER_OF_CURRENT_NOTES, len(self.order_products))]:
            self.show_row(product_info[0], product_info[1], product_info[2])
        self.lcdNumber.display(self.cost)

    def send_order(self):
        self.order = Order(self.input_name.displayText(), self.input_telephone.displayText(),
                           self.input_address.displayText(), self.order_products, self.cost)
        self.finish = FinishPage(self.order.send_order())
        self.setCentralWidget(self.finish)

    def buttons_connect(self):
        self.to_menu.clicked.connect(self.to_collect_order)
        self.forward.clicked.connect(self.forward_notes)
        self.back.clicked.connect(self.back_notes)
        self.make_order.clicked.connect(self.send_order)


class FinishPage(QMainWindow):
    def __init__(self, result):
        super().__init__()
        uic.loadUi('finish_page.ui', self)
        self.telephone.setText(result['telephone_number'])
        if result['error'] in ['Nonexistent dish', 'Not sale dish', 'Nonexistent version']:
            self.label.setText('Меню изменилось. Пожалуйста, закажите снова.')
            self.pushButton.clicked.connect(self.restart)
        elif result['error'] != 'OK':
            self.label.setText('Ошибка при отправке заказа, повторите')
        self.pushButton.clicked.connect(self.restart)
        self.setFixedSize(self.size())

    def restart(self):
        self.ex = CollectOrder(get_menu())
        self.setCentralWidget(self.ex)


def get_menu():
    menu = {'Всё': []}
    response = requests.get(f'{PIZZERIA_ADDRESS}/menu')
    json_response = response.json()
    for type_of_product in json_response.keys():
        if type_of_product not in menu.keys():
            menu[type_of_product] = []
        for product in json_response[type_of_product]:
            if 'add_info' in product.keys():
                menu[type_of_product].append(Product(type_of_product,
                                                     product['name'], product['proportions'], product['add_info']))
                menu['Всё'].append(menu[type_of_product][-1])
            else:
                menu[type_of_product].append(Product(type_of_product,
                                                     product['name'], product['proportions']))
                menu['Всё'].append(menu[type_of_product][-1])
    return menu


if __name__ == '__main__':
    appF = QApplication(sys.argv)
    ex = CollectOrder(get_menu())
    ex.show()
    sys.exit(appF.exec())
