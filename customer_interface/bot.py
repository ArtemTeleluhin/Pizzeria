# Импортируем необходимые классы.
from requests import post
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
import requests
from main import Product

TOKEN = '1721603616:AAG1KPzrBx5ANrIVXwviEneB4kOil-LYAtk'
PIZZERIA_ADDRESS = "http://127.0.0.1:8080"
COMMANDS = ["Мои команды:",
            "/menu - получить меню нашей пиццерии",
            "/name - ввести имя заказчика",
            "/telephone - ввести телефон заказчика",
            "/user_info - ввести информацию о заказчике (без этого заказ не будет оформлен)"
            "/address - ввести адрес доставки",
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


order = {'name': None,
         'telephone_number': None,
         'address': None}
menu = {}


def start(update, context):
    update.message.reply_text("Привет! Я бот, помогающий сделать заказ в пиццерию.\n" + '\n'.join(COMMANDS))


def help(update, context):
    update.message.reply_text('\n'.join(COMMANDS))


def get_menu(update, context):
    response = requests.get(f'{PIZZERIA_ADDRESS}/menu')
    json_response = response.json()
    text = []
    global menu
    cnt = 0
    for type_of_product in json_response.keys():
        text.append('')
        text.append(type_of_product)
        menu[type_of_product] = []
        for product in json_response[type_of_product]:
            if 'add_info' in product.keys():
                cur_product = BotProduct(type_of_product,
                                         product['name'], product['proportions'], product['add_info'])
            else:
                cur_product = BotProduct(type_of_product,
                                         product['name'], product['proportions'])
            menu[type_of_product].append((cur_product, cnt))
            cnt += 1
            text.append(f"id: {cnt - 1}   " + cur_product.output_format())

    update.message.reply_text('\n'.join(text))


def main():
    updater = Updater(TOKEN, use_context=True)
    # добавление информации о пользователе
    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("menu", get_menu))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
