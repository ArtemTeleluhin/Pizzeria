# Импортируем необходимые классы.
from requests import post
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler
import requests
from customer_interface import Product

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


def start(update, context):
    update.message.reply_text("Привет! Я бот, помогающий сделать заказ в пиццерию.\n" + '\n'.join(COMMANDS))


def help(update, context):
    update.message.reply_text('\n'.join(COMMANDS))


def main():
    updater = Updater(TOKEN, use_context=True)
    # добавление информации о пользователе
    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
