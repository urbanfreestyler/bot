from telebot.types import LabeledPrice

from bot.util import *
from database.models import Users, Transaction
from global_var import TEST_CLICK_TOKEN, TEST_PAYME_TOKEN
from project_configuration import logging


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons"
                                                                                                       ".Account"
                                                                                                       ".BALANCE"))
@bot.message_handler(commands=Commands.MY_BALANCE)
@logging()
def my_balance(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} use my balance')
    if db_util.get_user_status(chat_id=chat_id) != db_util.Constants.STATUSES[2]:
        delete_message(chat_id=message.chat.id,
                       message=message)
        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id="Buttons.Account.BalanceMenu")
                     .format(str(get_user_balance(chat_id=chat_id))),
                     reply_markup=markups.balance_menu(chat_id=chat_id))


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons"
                                                                                                       ".Menu"
                                                                                                       ".Balance.Add"))
def get_sum_to_add(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    if db_util.get_user_status(chat_id=chat_id) != db_util.Constants.STATUSES[2]:
        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id="Buttons.Account.SumToAdd"),
                     method=payment_type_choice,
                     reply_markup=markups.add_sum(chat_id=chat_id))


global sum_to_add
sum_to_add = 0


def payment_type_choice(message: Message):
    if message.text == Tx.get(message.chat.id, 'Buttons.Direction.BACK'):
        delete_message(chat_id=message.chat.id,
                       message=message)
        send_message(chat_id=message.chat.id,
                     text=Tx.get(chat_id=message.chat.id,
                                 text_id='Buttons.Account.BalanceMenu')
                     .format(get_user_balance(chat_id=message.chat.id)),
                     reply_markup=markups.balance_menu(chat_id=message.chat.id))
    elif message.text.isdigit():
        global sum_to_add
        sum_to_add = int(message.text)
        user = Users.get(Users.id == message.chat.id)
        send_message(chat_id=message.chat.id,
                     text=Tx.get(chat_id=message.chat.id,
                                 text_id='Buttons.Account.ADD_BALANCE'),
                     reply_markup=markups.add_balance_menu(chat_id=message.chat.id))
    else:
        send_message(chat_id=message.chat.id,
                     text=Tx.get(
                         chat_id=message.chat.id,
                         text_id='BotMessages.OnlyNumber'
                     ),
                     method=payment_type_choice)


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons"
                                                                                                       ".Menu"
                                                                                                       ".Click"))
def click_pay(message: Message):
    """
        Оплата через Click
    """

    prices = [LabeledPrice(label='Пополнить на 10000 сум', amount=sum_to_add * 100)]

    chat_id, text, message_id = get_info_from_message(message=message)

    bot.send_invoice(message.chat.id, title="Оплата Click",
                     description='Нажмите на кнопку ниже для пополнения баланса. '
                                 'Бот не получает никаких личных данных и операция проводится со стороны CLICK.',
                     provider_token=TEST_CLICK_TOKEN,
                     currency='uzs',
                     # photo_url='http://erkelzaar.tsudao.com/models/perrotta/TIME_MACHINE.jpg',
                     # photo_height=512,  # !=0/None or picture won't be shown
                     # photo_width=512,
                     # photo_size=512,
                     # is_flexible=False,  # True If you need to set up Shipping Fee
                     prices=prices,
                     # start_parameter='time-machine-example',
                     invoice_payload='ADD BALANCE')


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons"
                                                                                                       ".Menu"
                                                                                                       ".Payme"))
def payme_pay(message: Message):
    """
        Оплата через Payme
    """

    prices = [LabeledPrice(label=""'Пополнить на ' + str(sum_to_add) + ' сум'"", amount=sum_to_add * 100)]

    chat_id, text, message_id = get_info_from_message(message=message)

    bot.send_invoice(message.chat.id, title="Оплата Payme",
                     description='Нажмите на кнопку ниже для пополнения баланса. '
                                 'Бот не получает никаких личных данных и операция проводится со стороны Payme.',
                     provider_token=TEST_PAYME_TOKEN,
                     currency='uzs',
                     # photo_url='http://erkelzaar.tsudao.com/models/perrotta/TIME_MACHINE.jpg',
                     # photo_height=512,  # !=0/None or picture won't be shown
                     # photo_width=512,
                     # photo_size=512,
                     # is_flexible=False,  # True If you need to set up Shipping Fee
                     prices=prices,
                     # start_parameter='time-machine-example',
                     invoice_payload='ADD BALANCE',
                     )


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected "
                                                "your credentials, "
                                                " try to pay again in a few minutes, we need a small rest.")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    user = Users.get(Users.id == message.chat.id)
    user.balance += int(message.successful_payment.total_amount / 100)
    user.save()

    Transaction.create(user_id=message.chat.id,
                       trans_sum=sum_to_add,
                       trans_type=False)

    bot.send_message(chat_id=message.chat.id,
                     text=Tx.get(chat_id=message.chat.id,
                                 text_id='Buttons.Account.Balance.SuccessPayment').format(
                         str(int(message.successful_payment.total_amount / 100)), user.balance),
                     parse_mode='Markdown',
                     reply_markup=markups.balance_menu(chat_id=message.chat.id))


def get_user_balance(chat_id: int):
    user = db_util.Users.get(id=chat_id)
    balance = user.balance

    return balance


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons"
                                                                                                       ".Menu"
                                                                                                       ".Balance."
                                                                                                       "Withdraw"))
@logging()
def withdraw_money(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} use withdraw balance')
    user = Users.get(Users.id == chat_id)

    send_message(chat_id=chat_id,
                 text=Tx.get(chat_id=chat_id,
                             text_id="Buttons.Account.WITHDRAW_AMOUNT").format(
                     user.balance
                 ),
                 reply_markup=markups.withdraw_menu(chat_id=chat_id),
                 method=withdraw_check)


def withdraw_check(message: Message):
    if message.text.isdigit():

        user = Users.get(Users.id == message.chat.id)

        w_sum = int(message.text)

        if user.balance < w_sum:
            send_message(chat_id=message.chat.id,
                         text="На вашем балансе меньше денег, чем вы хотите вывести."
                              "Введите сумму, не превышающую ваш баланс.",
                         reply_markup=markups.withdraw_menu(chat_id=message.chat.id),
                         method=withdraw_check)

        else:
            user.balance -= w_sum
            user.save()

            Transaction.create(
                user_id=message.chat.id,
                trans_sum=w_sum,
                trans_type=True
            )
            send_message(chat_id=message.chat.id,
                         text=Tx.get(chat_id=message.chat.id,
                                     text_id='BotMessages.WithdrawSuccess').
                         format(w_sum, user.balance),
                         reply_markup=markups.balance_menu(chat_id=message.chat.id))

    elif message.text == Tx.get(message.chat.id, 'Buttons.Direction.BACK'):
        delete_message(chat_id=message.chat.id,
                       message=message)
        send_message(chat_id=message.chat.id,

                     text=Tx.get(chat_id=message.chat.id,

                                 text_id='Buttons.Account.BalanceMenu')
                     .format(get_user_balance(chat_id=message.chat.id)),

                     reply_markup=markups.balance_menu(chat_id=message.chat.id))

    else:
        send_message(chat_id=message.chat.id,
                     text=Tx.get(
                         chat_id=message.chat.id,
                         text_id='BotMessages.OnlyNumber'
                     ),
                     reply_markup=markups.withdraw_menu(chat_id=message.chat.id),
                     method=withdraw_check)


# ############################  РАБОТА С КАРТАМИ ПОЛЬЗОВАТЕЛЕЙ  ###################


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons"
                                                                                                       ".Account"
                                                                                                       ".Card"))
@logging()
def my_card_menu(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} entering my_card_menu')

    user_card = Users.get(Users.id == chat_id).card

    send_message(chat_id=chat_id,
                 text=Tx.get(chat_id=chat_id,
                             text_id='BotMessages.CardInfo'),
                 reply_markup=markups.my_card_menu(chat_id=chat_id))

    if user_card:
        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id='BotMessages.YourCard')
                     .format(user_card))


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons"
                                                                                                       ".Account"
                                                                                                       ".AddCard"))
@logging()
def add_card(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} entered add_card')
    send_message(chat_id=chat_id,
                 text=Tx.get(chat_id=chat_id,
                             text_id='BotMessages.AddCard'),
                 reply_markup=markups.add_card(chat_id=chat_id),
                 method=set_card)


def set_card(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=chat_id, text_id="Buttons.Direction.BACK"):
        delete_message(chat_id=message.chat.id,
                       message=message)
        send_message(chat_id=message.chat.id,

                     text=Tx.get(chat_id=message.chat.id,

                                 text_id='BotMessages.CardInfo')
                     .format(get_user_balance(chat_id=message.chat.id)),

                     reply_markup=markups.my_card_menu(chat_id=message.chat.id))

    elif text[0:4] == '9860' or text[0:4] == '8600':
        if len(text) == 16:
            global card_number
            card_number = text
            confirm_card_number(chat_id=chat_id)
        else:
            invalid_card_number(chat_id=chat_id)

    else:
        invalid_card_number(chat_id=chat_id)


def invalid_card_number(chat_id: int):
    send_message(chat_id=chat_id,
                 text=Tx.get(chat_id=chat_id,
                             text_id="BotMessages.InvalidCardNumber"),
                 reply_markup=markups.add_card(chat_id=chat_id),
                 method=set_card)


def confirm_card_number(chat_id: int):
    send_message(chat_id=chat_id,
                 text=Tx.get(chat_id=chat_id,
                             text_id="BotMessages.ConfirmCardNumber")
                 .format(card_number),
                 reply_markup=markups.confirm_card_number(chat_id=chat_id),
                 method=card_success)


def card_success(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    if text == Tx.get(chat_id=chat_id, text_id='Buttons.YES'):
        user = Users.get(Users.id == chat_id)
        user.card = card_number
        user.save()

        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id="BotMessages.CardAddedSuccessfully")
                     .format(user.card),
                     method=my_balance,
                     reply_markup=markups.balance_menu(chat_id=chat_id))

    elif text == Tx.get(chat_id=chat_id, text_id='Buttons.NO'):
        delete_message(message=message)
        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id='BotMessages.AddCard'),
                     reply_markup=markups.add_card(chat_id=chat_id),
                     method=set_card)

    else:
        delete_message(message=message)
        confirm_card_number(chat_id=chat_id)


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons"
                                                                                                       ".Account"
                                                                                                       ".DeleteCard"))
@logging()
def delete_card(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    user_card = Users.get(Users.id == chat_id).card

    if user_card:
        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id="BotMessages.DeleteCardQuestion")
                     .format(user_card),
                     reply_markup=markups.confirm_card_number(chat_id=chat_id),
                     method=card_deletion)
    else:
        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id="BotMessages.YouHaveNoCard"),
                     reply_markup=markups.my_card_menu(chat_id=chat_id),
                     method=my_card_menu)


def card_deletion(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=chat_id, text_id='Buttons.YES'):
        user = Users.get(Users.id == chat_id)
        user.card = ''
        user.save()

        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id="BotMessages.CardDeletedSuccessfully")
                     .format(user.card),
                     method=my_balance,
                     reply_markup=markups.balance_menu(chat_id=chat_id))

    elif text == Tx.get(chat_id=chat_id, text_id='Buttons.NO'):
        delete_message(message=message)
        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id='BotMessages.CardInfo'),
                     reply_markup=markups.my_card_menu(chat_id=chat_id),
                     method=my_card_menu)

    else:
        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id="BotMessages.ChooseFromKeyboard"),
                     method=card_deletion)


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id,
                                                                 text_id="Buttons.Account.TransactionHistory"))
@logging()
def get_transactions(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    logger.info(f'User {chat_id} entering transaction_history')

    transactions = Transaction.select().where(Transaction.user_id == chat_id)

    if transactions:
        for transaction in transactions:
            send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id,
                                     text_id="BotMessages.TransactionInfo")
                         .format(transaction.id,
                                 'Пополнение' if transaction.trans_type == 0 else 'Вывод',
                                 transaction.trans_sum,
                                 transaction.trans_date))
    else:
        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id="BotMessages.NoTransactionsYet"))
