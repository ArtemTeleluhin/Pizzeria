from flask import Flask, jsonify
from server.data import db_session
from server.data.categories import Categories
from server.data.dishes import Dishes
from server.data.versions import Versions

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


if __name__ == '__main__':
    db_session.global_init(f'db/{DB_NAME}.db')
    app.run(port=8080, host='127.0.0.1', debug=True)
