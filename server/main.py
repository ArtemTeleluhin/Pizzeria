from flask import Flask, jsonify, request
from server.data import db_session
from server.data.categories import Categories
from server.data.dishes import Dishes
from server.data.versions import Versions
from server.data.orders import Orders
from server.data.versions_to_orders import VersionsToOrders
import json
import datetime

DB_NAME = 'pizzeria_base'
PIZZERIA_PARAMETERS = 'pizzeria_parameters'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/menu')
def menu():
    db_sess = db_session.create_session()
    menu = dict()
    for category in db_sess.query(Categories).all():
        menu[category.name] = []
        for dish in category.dishes:
            if dish.is_sale:
                dish_dict = dict()
                dish_dict['name'] = dish.name
                if dish.add_info:
                    dish_dict['add_info'] = dish.add_info
                dish_dict['proportions'] = []
                for version in dish.versions:
                    dish_dict['proportions'].append({
                        'size': version.size,
                        'price': version.price
                    })
                if dish_dict['proportions']:
                    menu[category.name].append(dish_dict)
        if not menu[category.name]:
            menu.pop(category.name)
    return jsonify(menu)


@app.route('/make_order', methods=['POST'])
def make_order():
    parameters = load_pizzeria_parameters()
    telephone_number = parameters['telephone_number']
    if not request.json:
        return jsonify({'error': 'Empty request', 'telephone_number': telephone_number})
    for key in ['name', 'telephone_number', 'address', 'sum_price', 'order']:
        if key not in request.json:
            return jsonify({'error': 'Have not parameter',
                            'parameter': key,
                            'telephone_number': telephone_number})
    if not request.json['order']:
        return jsonify({'error': 'Empty order', 'telephone_number': telephone_number})
    db_sess = db_session.create_session()
    for dish_dict in request.json['order']:
        dish = db_sess.query(Dishes).filter(Dishes.name == dish_dict['name']).first()
        if not dish:
            return jsonify({'error': 'Nonexistent dish', 'telephone_number': telephone_number})
        if not dish.is_sale:
            return jsonify({'error': 'Not sale dish', 'telephone_number': telephone_number})
        version = db_sess.query(Versions).filter(Versions.dish == dish,
                                                 Versions.size == dish_dict['size']).first()
        if not version:
            return jsonify({'error': 'Nonexistent version', 'telephone_number': telephone_number})

    start_time = datetime.datetime.strptime(parameters['start_time'], '%H:%M').time()
    end_time = datetime.datetime.strptime(parameters['end_time'], '%H:%M').time()
    if not (start_time <= datetime.datetime.now().time() <= end_time):
        return jsonify({'error': 'Not working time', **parameters})

    order = Orders()
    if request.json['name']:
        order.customer_name = request.json['name']
    if request.json['telephone_number']:
        order.telephone_number = request.json['telephone_number']
    order.address = request.json['address']
    order.sum_price = request.json['sum_price']
    db_sess.add(order)
    db_sess.commit()
    for dish_dict in request.json['order']:
        dish = db_sess.query(Dishes).filter(Dishes.name == dish_dict['name']).first()
        version = db_sess.query(Versions).filter(Versions.dish == dish,
                                                 Versions.size == dish_dict['size']).first()
        versions_to_orders = VersionsToOrders()
        versions_to_orders.version = version
        versions_to_orders.order = order
        versions_to_orders.count = dish_dict['count']
        db_sess.add(versions_to_orders)
        db_sess.commit()
    return jsonify({'error': 'OK', 'telephone_number': telephone_number})


@app.route('/pizzeria_parameters')
def pizzeria_parameters():
    data = load_pizzeria_parameters()
    return jsonify(data)


def load_pizzeria_parameters():
    with open(f'db/{PIZZERIA_PARAMETERS}.json') as file:
        data = json.load(file)
        return data


if __name__ == '__main__':
    db_session.global_init(f'db/{DB_NAME}.db')
    app.run(port=8080, host='127.0.0.1', debug=True)
