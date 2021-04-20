from flask import Flask, jsonify, request
from server.data import db_session
from server.data.categories import Categories
from server.data.dishes import Dishes
from server.data.versions import Versions
from server.data.orders import Orders
from server.data.versions_to_orders import VersionsToOrders

DB_NAME = 'pizzeria_base'

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
    if not request.json:
        return jsonify({'error': 'Empty request'})
    for key in ['name', 'telephone_number', 'address', 'sum_price', 'order']:
        if key not in request.json:
            return jsonify({'error': 'Have not parameter', 'parameter': key})
    if not request.json['order']:
        return jsonify({'error': 'Empty order'})
    db_sess = db_session.create_session()
    for dish_dict in request.json['order']:
        dish = db_sess.query(Dishes).filter(Dishes.name == dish_dict['name']).first()
        if not dish:
            return jsonify({'error': 'Nonexistent dish'})
        if not dish.is_sale:
            return jsonify({'error': 'Not sale dish'})
        version = db_sess.query(Versions).filter(Versions.dish == dish,
                                                 Versions.size == dish_dict['size']).first()
        if not version:
            return jsonify({'error': 'Nonexistent version'})
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
    return jsonify({'error': 'OK'})


if __name__ == '__main__':
    db_session.global_init(f'db/{DB_NAME}.db')
    app.run(port=8080, host='127.0.0.1', debug=True)
