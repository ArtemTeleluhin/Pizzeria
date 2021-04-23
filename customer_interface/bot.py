# Импортируем необходимые классы.
from requests import post
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
import requests
from main import Product

TOKEN = '1721603616:AAG1KPzrBx5ANrIVXwviEneB4kOil-LYAtk'
PIZZERIA_ADDRESS = input().rstrip()  # "http://127.0.0.1:8080"
COMMANDS = ["Мои команды:",
            "/menu - получить меню нашей пиццерии",
            "/user_info - ввести информацию о заказчике (без этого заказ не будет оформлен)",
            "/add_product - добавить продукт в корзину",
            "/show_basket - показать выбранные продукты",
            "/order - сделать заказ (предварительно нужно ввести имя, телефон и адрес доставки)"]


class BotProduct(Product):
    def __init__(self, type_of_product, name, proportions, add_info=''):
        super().__init__(type_of_product, name, proportions, add_info)

    def output_format(self):
        ans = f"{self.name}   {self.add_info}"
        if self.add_info != '':
            ans += '    '
        for i, proportion in enumerate(self.proportions):
            ans += f'{str(i + 1)}) {proportion["size"]} - {proportion["price"]}   '
        return ans


order = {}
menu = {}


def start(update, context):
    global order, menu
    if update.message.chat_id not in order.keys():
        order[update.message.chat_id] = {'name': None,
                                         'telephone_number': None,
                                         'address': None}
        menu[update.message.chat_id] = {}
    update.message.reply_text("Привет! Я бот, помогающий сделать заказ в пиццерию.\n" + '\n'.join(COMMANDS))


def help(update, context):
    update.message.reply_text('\n'.join(COMMANDS))


def get_menu(update, context):
    global menu, order
    if update.message.chat_id not in order.keys():
        order[update.message.chat_id] = {'name': None,
                                         'telephone_number': None,
                                         'address': None}
        menu[update.message.chat_id] = {}
    response = requests.get(f'{PIZZERIA_ADDRESS}/menu')
    json_response = response.json()
    text = []

    cnt = 0
    for type_of_product in json_response.keys():
        text.append('')
        text.append(type_of_product)
        menu[update.message.chat_id][type_of_product] = []
        for product in json_response[type_of_product]:
            if 'add_info' in product.keys():
                cur_product = BotProduct(type_of_product,
                                         product['name'], product['proportions'], product['add_info'])
            else:
                cur_product = BotProduct(type_of_product,
                                         product['name'], product['proportions'])
            menu[update.message.chat_id][type_of_product].append((cur_product, cnt))
            cnt += 1
            text.append(f"id: {cnt - 1}   " + cur_product.output_format())

    update.message.reply_text('\n'.join(text))


def make_order(update, context):
    get_json = get_order_products(update)
    global order
    for key in order[update.message.chat_id].keys():
        get_json[key] = order[update.message.chat_id][key]
    result = post('http://127.0.0.1:8080/make_order', json=get_json).json()
    if result['error'] in ['Nonexistent dish', 'Not sale dish', 'Nonexistent version']:
        update.message.reply_text("Меню изменилось. Пожалуйста, закажите снова")
    elif result['error'] == 'Empty order':
        update.message.reply_text("Не выбрано никаких блюд. Невозможно сделать заказ")
    elif result['error'] == 'Have not parameter':
        update.message.reply_text("Не заполнена информация о заказчике. Пожалуйста, заполните ее и повторите попытку")
    elif result['error'] == 'OK':
        update.message.reply_text("Заказ успешно получен)")


# добавление информации о пользователе
# 0
def name(update, context):
    update.message.reply_text('Введите имя')
    return 1


# 1
def get_name(update, context):
    global order
    order[update.message.chat_id]['name'] = update.message.text
    update.message.reply_text('Введите телефон')
    return 2


# 2
def get_telephone(update, context):
    global order
    order[update.message.chat_id]['telephone'] = update.message.text
    update.message.reply_text('Введите адрес')
    return 3


# 3
def get_address(update, context):
    global order
    order[update.message.chat_id]['telephone'] = update.message.text
    update.message.reply_text('Готово)')
    return ConversationHandler.END


# Добавление продукта
# 0
def get_name_product_info(update, context):
    update.message.reply_text("Введите id продукта")
    return 1


# 1
def get_name_product(update, context):
    global menu
    current_product = update.message.text
    for type_of_product in menu[update.message.chat_id].keys():
        for product, product_id in menu[update.message.chat_id][type_of_product]:
            # print(product.get_name(), product_id)
            if current_product == str(product_id):
                context.user_data['current_product'] = product
                if len(product.get_proportion()) > 1:
                    update.message.reply_text(
                        "Отлично) а теперь номер размерности продукта (указан перед каждой размерностью)")
                    return 3
                else:
                    update.message.reply_text(
                        "Супер) а теперь количество, которое хотите добавить в заказ." +
                        " Если продукт был добавлен раньше, укажите его новое количество.")
                    return 5
    update.message.reply_text("Такого продукта не нашлось, введите еще раз")
    return 1


# 3
def get_proportion_product(update, context):
    context.user_data['current_proportion'] = update.message.text
    if not context.user_data['current_proportion'].isdigit() or len(
            context.user_data['current_product'].get_proportion()) < int(context.user_data['current_proportion']):
        update.message.reply_text("Не понимаю, какую размерность вы имеете ввиду")
        return 3
    update.message.reply_text(
        "Супер) а теперь количество, которое хотите добавить в заказ." +
        " Если продукт был добавлен раньше, укажите его новое количество.")
    return 5


# 5
def get_number_product(update, context):
    val = update.message.text
    if not val.isdigit():
        update.message.reply_text("Вы ввели количество, которое я не могу понять(\n Введите одну цифру")
        return 5
    context.user_data['current_product'].set_proportion(int(context.user_data['current_proportion']) - 1, val)
    update.message.reply_text("Готово)")
    return ConversationHandler.END


def get_order_products(update):
    global menu
    order_products = {'sum_price': 0}
    print(order_products['sum_price'])
    for type_of_product in menu[update.message.chat_id].keys():
        for product, product_id in menu[update.message.chat_id][type_of_product]:
            for j, proportion in enumerate(product.get_proportion()):
                if product.take_number_of_proportion(j) != 0:
                    if 'order' not in menu[update.message.chat_id].keys():
                        order_products['order'] = []
                    order_products['order'].append(
                        {'name': product.get_name(), 'size': proportion['size'], 'price': proportion['price'],
                         'count': product.take_number_of_proportion(j)})
                    order_products['sum_price'] += int(
                        int(product.take_number_of_proportion(j)) * int(proportion['price']))
    return order_products


def show_basket(update, context):
    text = []
    for product_info in get_order_products(update)['order']:
        string_formatted = []
        for key in product_info.keys():
            string_formatted.append(str(product_info[key]))
        text.append('   '.join(string_formatted))
    text.append(f"Общая сумма: {get_order_products(update)['sum_price']}")
    update.message.reply_text('\n'.join(text))


def main():
    updater = Updater(TOKEN, use_context=True)
    # добавление информации о пользователе
    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    user_information = ConversationHandler(
        entry_points=[CommandHandler('user_info', name)],
        states={
            1: [MessageHandler(Filters.text, get_name, pass_user_data=True)],
            2: [MessageHandler(Filters.text, get_telephone, pass_user_data=True)],
            3: [MessageHandler(Filters.text, get_address, pass_user_data=True)],
        },
        fallbacks=[MessageHandler(Filters.text, get_address)]
    )
    dp.add_handler(user_information)

    # добавление продукта в корзину
    add_product = ConversationHandler(
        entry_points=[CommandHandler('add_product', get_name_product_info)],
        states={
            1: [MessageHandler(Filters.text, get_name_product, pass_user_data=True)],
            3: [MessageHandler(Filters.text, get_proportion_product, pass_user_data=True)],
            5: [MessageHandler(Filters.text, get_number_product, pass_user_data=True)],
        },
        fallbacks=[MessageHandler(Filters.text, get_number_product)]
    )
    dp.add_handler(add_product)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("show_basket", show_basket))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("menu", get_menu))
    dp.add_handler(CommandHandler("order", make_order))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
