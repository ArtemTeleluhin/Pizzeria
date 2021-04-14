from flask import Flask
from server.data import db_session
from server.data.categories import Categories
from server.data.dishes import Dishes
from server.data.versions import Versions

MENU = {
    'Пиццы': [
        {
            'name': 'Маргарита',
            'proportions': [
                {
                    'size': '25 см',
                    'price': 150
                },
                {
                    'size': '35 см',
                    'price': 200
                },
                {
                    'size': '45 см',
                    'price': 250
                }
            ],
            'add_info': 'Помидоры, сыр Моцарелла, базилик, томатный соус'
        },
        {
            'name': 'Пепперони',
            'proportions': [
                {
                    'size': '25 см',
                    'price': 150
                },
                {
                    'size': '35 см',
                    'price': 200
                },
                {
                    'size': '45 см',
                    'price': 250
                }
            ],
            'add_info': 'Колбаса, томатный соус, сыр'
        },
        {
            'name': 'Мясная',
            'proportions': [
                {
                    'size': '25 см',
                    'price': 150
                },
                {
                    'size': '35 см',
                    'price': 200
                },
                {
                    'size': '45 см',
                    'price': 250
                }
            ],
            'add_info': 'Ветчина, колбаса, томатный соус, сыр'
        }
    ],
    'Напитки': [
        {
            'name': 'Кока-Кола',
            'proportions': [
                {
                    'size': '0.3 л',
                    'price': 45
                },
                {
                    'size': '0.7 л',
                    'price': 90
                },
                {
                    'size': '1 л',
                    'price': 110
                }
            ]
        },
        {
            'name': 'Яблочный сок',
            'proportions': [
                {
                    'size': '0.3 л',
                    'price': 40
                },
                {
                    'size': '0.7 л',
                    'price': 80
                },
                {
                    'size': '1 л',
                    'price': 100
                }
            ]
        }
    ],
    'Десерты': [
        {
            'name': 'Маффин',
            'proportions': [
                {
                    'size': 'Обычный',
                    'price': 50
                }
            ]
        },
        {
            'name': 'Круассан с шоколадом',
            'proportions': [
                {
                    'size': 'Обычный',
                    'price': 60
                }
            ]
        }
    ]
}

DB_NAME = 'pizzeria_base'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

if __name__ == '__main__':
    db_session.global_init(f'db/{DB_NAME}.db')
    db_sess = db_session.create_session()

    for category_name in MENU:
        category = Categories()
        category.name = category_name
        db_sess.add(category)
        db_sess.commit()
        for dish_obj in MENU[category_name]:
            dish = Dishes()
            dish.name = dish_obj['name']
            if 'add_info' in dish_obj:
                dish.add_info = dish_obj['add_info']
            dish.category = category
            db_sess.add(dish)
            db_sess.commit()
            for version_obj in dish_obj['proportions']:
                version = Versions()
                version.size = version_obj['size']
                version.price = version_obj['price']
                version.dish = dish
                db_sess.add(version)
                db_sess.commit()
