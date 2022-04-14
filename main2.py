import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove
import sqlite3
from pyqiwip2p import QiwiP2P

BOT_TOKEN = '5009162225:AAERkKTZ1im3YBvKuNFF3rEp_EvzJYrSXb4'

QIWI_TOKEN = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6ImFxaXd2ZS0wMCIsInVzZXJfaWQiOiI5OTI0MDAwMjI4MDkiLCJzZWNyZXQiOiIwZTg0OTBlNGJkNzI3OWVmM2UyZDNmN2RjMjA5ODM5ZTVhY2NjMDI0YWExNmZhZjUzNmM5ZGU5OTc3NjY1NjQ4In19'

CHANNEL_ID = -1001580872307

admin_ids = [1894088037]

db_path = 'data.db'

p2p = QiwiP2P(auth_key=QIWI_TOKEN)

bot = telebot.TeleBot(BOT_TOKEN)

with sqlite3.connect(db_path) as con:
    cursor = con.cursor()
    price_data = cursor.execute('SELECT price FROM info').fetchone()[0]

price = price_data


def get_balance(user_id):
    with sqlite3.connect(db_path) as con:
        cursor = con.cursor()
        money = cursor.execute('SELECT money FROM users WHERE user_id = (?)', (user_id,)).fetchone()[0]
    return money


def add_payment_to_db(bill_id, user_id, amount):
    with sqlite3.connect(db_path) as con:
        cursor = con.cursor()
        cursor.execute('INSERT INTO payments (bill_id, user_id, amount) VALUES ((?), (?), (?))',
                       (bill_id, user_id, amount))


def add_money(user_id, amount):
    with sqlite3.connect(db_path) as con:
        cursor = con.cursor()
        cursor.execute('UPDATE users SET money = (?) WHERE user_id = (?)',
                       (cursor.execute('SELECT money FROM users WHERE user_id = (?)', (user_id,)).fetchone()[0] + float(
                           amount), user_id))


def pay_money(user_id, PRICE):
    with sqlite3.connect(db_path) as con:
        cursor = con.cursor()
        cursor.execute('UPDATE users SET money = (?) WHERE user_id = (?)',
                       (cursor.execute('SELECT money FROM users WHERE user_id = (?)', (user_id,)).fetchone()[0] - PRICE,
                        user_id))


def generate_payment(message, amount):
    comment = f"{message.chat.id}_{message.message_id}"

    bill = p2p.bill(amount=amount, comment=comment)

    add_payment_to_db(bill.bill_id, message.chat.id, amount)

    bot.delete_message(message.chat.id, message.message_id - 1)
    bot.delete_message(message.chat.id, message.message_id)

    # bot.send_message(message.chat.id, '========== Главное-меню ==========', reply_markup=main_keyboard)
    return bot.send_message(message.chat.id,
                            f'<b>Отправьте <u>{amount}</u> рублей на счет QIWI\nСсылка на оплату: <i>{bill.pay_url}</i></b>',
                            parse_mode='HTML',
                            reply_markup=buy_menu(isUrl=True, url=bill.pay_url, bill_id=bill.bill_id))

    # return bot.send_message(message.chat.id, 'Оплата на карту в разработке',
    #                         reply_markup=pay_card_keyboard)


def get_amount(message):
    try:
        if message.text == 'Отменить':
            bot.send_message(message.chat.id, 'Действие отменено', reply_markup=ReplyKeyboardRemove())
            return bot.send_message(message.chat.id, '========== Главное-меню ==========', reply_markup=main_keyboard)

        amount = int(message.text)
        if amount < 5:
            bot.send_message(message.chat.id, 'Минимальная сумма пополнения: 5 рубль')
            return bot.send_message(message.chat.id, '========== Главное-меню ==========', reply_markup=main_keyboard)

        if amount > 15000:
            bot.send_message(message.chat.id, 'Максимальная сумма пополнения: 15,000 рублей')
            return bot.send_message(message.chat.id, '========== Главное-меню ==========', reply_markup=main_keyboard)


    except ValueError:
        bot.send_message(message.chat.id, '<b>Вы ввели неправильное значение, попробуйте еще раз!</b>',
                         parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
        return bot.send_message(message.chat.id, '========== Главное-меню ==========', reply_markup=main_keyboard)

    generate_payment(message, amount)


def buy_menu(isUrl=False, url='', bill_id=''):
    keyboard = InlineKeyboardMarkup(row_width=1)

    if isUrl:
        keyboard.add(InlineKeyboardButton(text='Ссылка на оплату QIWI', url=url),
                     InlineKeyboardButton(text='Проверить оплату', callback_data=f'check_{bill_id}'),
                     InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
                     )

    return keyboard


pay_card_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Ссылка на оплтау', callback_data='1'),
    InlineKeyboardButton(text='Проверить оплату', callback_data='1')
)

main_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Создать объявление', callback_data='create')
).add(
    InlineKeyboardButton(text='Баланс', callback_data='balance'),
    InlineKeyboardButton(text='Пополнить', callback_data='top_up')
).add(
    InlineKeyboardButton(text='Прайс', callback_data='price'),
    InlineKeyboardButton(text='Перейти в канал', url='https://t.me/WB_i_Ozon'),
)

price_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Баланс', callback_data='balance'),
    InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
)

top_up_keyboard = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Пополнить', callback_data='top_up'),
    InlineKeyboardButton(text='Главное меню', callback_data='main_menu'),
)


def price_text(price):
    return f'Стоимость объявления: {price}₽'


admin_keyboard = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text='Изменить цену', callback_data='admin_change_price'),
    InlineKeyboardButton(text='Бонус пользователю', callback_data='admin_bonus'),
    InlineKeyboardButton(text='Рассылка', callback_data='admin_mail'),
    InlineKeyboardButton(text='Количество пользователей', callback_data='admin_count'),
)

confirm_mail_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton(text='Верно'),
    KeyboardButton(text='Отменить')
)

create_text = '''
Введите текст объявления.
Не забудьте указать контакты.'''
create_new_text = '''
Введите новый текст объявления.
Не забудьте указать контакты.'''


@bot.message_handler(commands=['start'])
def start(message):
    try:
        # bot.delete_message(message.chat.id, message.message_id)

        with sqlite3.connect(db_path) as con:
            cursor = con.cursor()
            cursor.execute('INSERT INTO users (user_id) VALUES ((?))', (message.chat.id,))
    except Exception as ex:
        print(ex)
        pass

    bot.send_message(message.chat.id,
                     'Добро пожаловать!\nВы зарегистрированы в боте и теперь можете размещать объявления.',
                     reply_markup=main_keyboard)


@bot.message_handler(commands=['admin'])
def admin(message):
    if message.chat.id in admin_ids:
        bot.send_message(message.chat.id, 'Админ Панель', reply_markup=admin_keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'create':
        bot.delete_message(call.message.chat.id, call.message.message_id)

        bot.send_message(call.message.chat.id, create_text,
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Отменить')))
        bot.register_next_step_handler(call.message, get_text)

    elif call.data == 'balance':
        bot.edit_message_text(f'Ваш баланс: {get_balance(call.message.chat.id)}₽', call.message.chat.id,
                              call.message.message_id, reply_markup=top_up_keyboard)

    elif call.data == 'price':
        bot.edit_message_text(price_text(price), call.message.chat.id, call.message.message_id,
                              reply_markup=price_keyboard)

    elif call.data == 'main_menu':
        bot.edit_message_text('========== Главное-меню ==========', call.message.chat.id, call.message.message_id,
                              reply_markup=main_keyboard)

    elif call.data == 'main_menu_photo':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, '========== Главное-меню ==========', reply_markup=main_keyboard)

    elif call.data == 'post':
        if get_balance(call.message.chat.id) >= price:
            pay_money(call.message.chat.id, price)

            bot.send_message(CHANNEL_ID, call.message.text,
                             reply_markup=InlineKeyboardMarkup(row_width=1).add(
                                 InlineKeyboardButton(text='НАПИСАТЬ АВТОРУ',
                                                      url=f'tg://user?id={call.message.chat.id}'),
                                 InlineKeyboardButton(text='РАЗМЕСТИТЬ ОБЪЯВЛЕНИЕ', url='https://t.me/WB_i_Ozon_BOT')))
            bot.send_message(call.message.chat.id, 'Ваш пост опубликовано')
            bot.send_message(call.message.chat.id, '========== Главное-меню ==========',
                             reply_markup=main_keyboard)
        else:
            bot.answer_callback_query(call.id,
                                      text=f'Недостаточно средств для оплаты\nПубликации ({price} руб.).\nВаш баланс: {get_balance(call.message.chat.id)}₽',
                                      show_alert=True)

    elif call.data == 'post_photo':
        if get_balance(call.message.chat.id) >= price:
            pay_money(call.message.chat.id, price)

            bot.send_photo(CHANNEL_ID, call.message.photo[0].file_id, caption=call.message.caption,
                           reply_markup=InlineKeyboardMarkup(row_width=1).add(
                               InlineKeyboardButton(text='НАПИСАТЬ АВТОРУ', url=f'tg://user?id={call.message.chat.id}'),
                               InlineKeyboardButton(text='РАЗМЕСТИТЬ ОБЪЯВЛЕНИЕ', url='https://t.me/WB_i_Ozon_BOT')))
            bot.send_message(call.message.chat.id, 'Ваш пост опубликовано')
            bot.send_message(call.message.chat.id, '========== Главное-меню ==========',
                             reply_markup=main_keyboard)
        else:
            bot.answer_callback_query(call.id,
                                      text=f'Недостаточно средств для оплаты\nПубликации ({price} руб.).\nВаш баланс: {get_balance(call.message.chat.id)}₽',
                                      show_alert=True)


    elif call.data == 'edit_post':
        bot.delete_message(call.message.chat.id, call.message.message_id)

        bot.send_message(call.message.chat.id, create_new_text,
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Отменить')))
        bot.register_next_step_handler(call.message, get_text)

    elif call.data == 'top_up':
        bot.delete_message(call.message.chat.id, call.message.message_id)

        bot.send_message(call.message.chat.id, '<b>Введите сумму</b>', parse_mode="HTML",
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Отменить')))
        bot.register_next_step_handler(call.message, get_amount)

    elif call.data.startswith('check'):
        bill_id = call.data[6:]
        amount = p2p.check(bill_id).amount

        with sqlite3.connect(db_path) as con:
            cursor = con.cursor()
            status = cursor.execute('SELECT status FROM payments WHERE bill_id = (?)', (bill_id,)).fetchone()[0]
        if status == 'sent':
            pass
        else:
            return bot.send_message(call.message.chat.id, 'На наш баланс уже зачислилась оплата за этот платеж')

        if str(p2p.check(bill_id=bill_id).status) == 'PAID':
            with sqlite3.connect(db_path) as con:
                cursor = con.cursor()
                cursor.execute('UPDATE payments SET status = "PAID" WHERE bill_id = (?)', (bill_id,))

            add_money(call.message.chat.id, amount)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, f'Ваш счет пополнен на {amount} рублей')
            bot.send_message(call.message.chat.id, f'Ваш баланс: {get_balance(call.message.chat.id)}₽',
                             reply_markup=top_up_keyboard)

        else:
            bot.answer_callback_query(call.id, 'Вы не оплатили счет!', show_alert=True)


    elif call.data == 'admin_change_price':
        bot.send_message(call.message.chat.id, '<b>Введите новую цену</b>', parse_mode='HTML',
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Отменить')))
        bot.register_next_step_handler(call.message, get_new_price)

    elif call.data == 'admin_bonus':
        bot.send_message(call.message.chat.id, '<b>Введите id пользователя</b>', parse_mode='HTML',
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Отменить')))
        bot.register_next_step_handler(call.message, get_bonus_id)

    elif call.data == 'admin_mail':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(call.message.chat.id, 'Отправьте текст, фото или видео для рассылки')
        bot.register_next_step_handler(call.message, get_mail_data)

    elif call.data == 'admin_count':
        try:
            with sqlite3.connect('data.db') as con:
                cursor = con.cursor()
                users = cursor.execute('SELECT user_id FROM users').fetchall()
            bot.send_message(call.message.chat.id, f'Всего пользователей - {len(users)}')
        except Exception as ex:
            print(ex)
            return bot.send_message(call.message.chat.id, 'Не удалось получить количество пользователей')

    elif call.data == 'pay_card':
        bot.send_message(call.message.chat.id, 'В разработке🕚')

    elif call.data == 'add_photo':
        text = call.message.text

        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, '<b>Отправьте изображение</b>', parse_mode='HTML',
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Назад')))
        bot.register_next_step_handler(call.message, get_photo, caption=text)

    elif call.data == 'remove_photo':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, '<b>Изображение удалено</b>', parse_mode='HTML')
        bot.send_message(call.message.chat.id, call.message.caption,
                         reply_markup=InlineKeyboardMarkup().add(
                             InlineKeyboardButton(text='Опубликовать', callback_data='post'),
                             InlineKeyboardButton(text='Редактировать', callback_data='edit_post')).add(
                             InlineKeyboardButton(text='Добавить фото', callback_data='add_photo')).add(
                             InlineKeyboardButton(text='Главное меню', callback_data='main_menu'))
                         )

    elif call.data == 'edit_photo_text':
        bot.send_message(call.message.chat.id, '<b>Введите новый текст объявления.\nНе забудьте указать контакты.</b>',
                         parse_mode='HTML')
        bot.register_next_step_handler(call.message, get_new_photo_text, file_id=call.message.photo[0].file_id,
                                       old_caption=call.message.caption)


def get_new_photo_text(message, **kwargs):
    if message.content_type == 'text':
        try:
            bot.send_message(message.chat.id, '<b>Текст редактирован</b>', parse_mode='HTML',
                             reply_markup=ReplyKeyboardRemove())
            bot.send_photo(message.chat.id, kwargs['file_id'], message.text,
                           reply_markup=InlineKeyboardMarkup().add(
                               InlineKeyboardButton(text='Опубликовать', callback_data='post_photo'),
                               InlineKeyboardButton(text='Редактировать текст', callback_data='edit_photo_text')).add(
                               InlineKeyboardButton(text='Убрать фото', callback_data='remove_photo')).add(
                               InlineKeyboardButton(text='Главное меню', callback_data='main_menu_photo'))
                           )

        except:
            bot.send_message(message.chat.id, 'Текст слишком большой для описания')
            bot.send_photo(message.chat.id, kwargs['file_id'], kwargs['old_caption'],
                           reply_markup=InlineKeyboardMarkup().add(
                               InlineKeyboardButton(text='Опубликовать', callback_data='post_photo'),
                               InlineKeyboardButton(text='Редактировать текст', callback_data='edit_photo_text')).add(
                               InlineKeyboardButton(text='Убрать фото', callback_data='remove_photo')).add(
                               InlineKeyboardButton(text='Главное меню', callback_data='main_menu_photo'))
                           )
    else:
        bot.send_message(message.chat.id, 'Вы отправили не текст')
        bot.send_photo(message.chat.id, kwargs['file_id'], kwargs['old_caption'],
                       reply_markup=InlineKeyboardMarkup().add(
                           InlineKeyboardButton(text='Опубликовать', callback_data='post_photo'),
                           InlineKeyboardButton(text='Редактировать текст', callback_data='edit_photo_text')).add(
                           InlineKeyboardButton(text='Убрать фото', callback_data='remove_photo')).add(
                           InlineKeyboardButton(text='Главное меню', callback_data='main_menu_photo'))
                       )


def get_photo(message, **kwargs):
    if message.content_type == 'photo':
        bot.delete_message(message.chat.id, message.message_id - 1)
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, '<b>Изображение добавлено</b>', parse_mode='HTML',
                         reply_markup=ReplyKeyboardRemove())
        bot.send_photo(message.chat.id, message.photo[0].file_id, caption=kwargs['caption'],
                       reply_markup=InlineKeyboardMarkup().add(
                           InlineKeyboardButton(text='Опубликовать', callback_data='post_photo'),
                           InlineKeyboardButton(text='Редактировать текст', callback_data='edit_photo_text')).add(
                           InlineKeyboardButton(text='Убрать фото', callback_data='remove_photo')).add(
                           InlineKeyboardButton(text='Главное меню', callback_data='main_menu_photo'))
                       )

    else:
        if message.text == 'Назад':
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, '<b>Действие отменено</b>', parse_mode='HTML',
                             reply_markup=ReplyKeyboardRemove())
            bot.send_message(message.chat.id, kwargs['caption'],
                             reply_markup=InlineKeyboardMarkup().add(
                                 InlineKeyboardButton(text='Опубликовать', callback_data='post'),
                                 InlineKeyboardButton(text='Редактировать текст', callback_data='edit_post')).add(
                                 InlineKeyboardButton(text='Добавить фото', callback_data='add_photo')).add(
                                 InlineKeyboardButton(text='Главное меню', callback_data='main_menu'))
                             )

        else:
            bot.send_message(message.chat.id, '<b>Вы отправили не изображение</b>', parse_mode='HTML',
                             reply_markup=ReplyKeyboardRemove())
            bot.send_message(message.chat.id, kwargs['caption'],
                             reply_markup=InlineKeyboardMarkup().add(
                                 InlineKeyboardButton(text='Опубликовать', callback_data='post'),
                                 InlineKeyboardButton(text='Редактировать текст', callback_data='edit_post')).add(
                                 InlineKeyboardButton(text='Добавить фото', callback_data='add_photo')).add(
                                 InlineKeyboardButton(text='Главное меню', callback_data='main_menu'))
                             )


# def get_text_2(message, **kwargs):
#    try:
#        message.text.lower()
#    except Exception as ex:
#        print(ex)
#        bot.send_message(message.chat.id, 'Вы прислали не текст, попробуйте еще раз!', reply_markup=ReplyKeyboardRemove())
#        bot.send_message(message.chat.id, kwargs['caption'],
#                             reply_markup=InlineKeyboardMarkup().add(
#                                 InlineKeyboardButton(text='Опубликовать', callback_data='post'),
#                                 InlineKeyboardButton(text='Редактировать', callback_data='edit_post')).add(
#                                 InlineKeyboardButton(text='Добавить фото', callback_data='add_photo')).add(
#                                 InlineKeyboardButton(text='Главное меню', callback_data='main_menu'))
#                                )
#
#    if message.text == 'Назад':
#            bot.delete_message(message.chat.id, message.message_id)
#            bot.send_message(message.chat.id, 'Действие отменено!', reply_markup=ReplyKeyboardRemove())
#            bot.send_message(message.chat.id, kwargs['caption'],
#                             reply_markup=InlineKeyboardMarkup().add(
#                                 InlineKeyboardButton(text='Опубликовать', callback_data='post'),
#                                 InlineKeyboardButton(text='Редактировать', callback_data='edit_post')).add(
#                                 InlineKeyboardButton(text='Добавить фото', callback_data='add_photo')).add(
#                                 InlineKeyboardButton(text='Главное меню', callback_data='main_menu'))
#                                )
#
#    if message.text.lower() != 'Назад':
#        bot.delete_message(message.chat.id, message.message_id-1)
#        bot.delete_message(message.chat.id, message.message_id)
#
# bot.send_message(message.chat.id, '======== ОБЪЯВЛЕНИЕ ========', reply_markup=ReplyKeyboardRemove())
#
#        bot.send_message(message.chat.id, message.text,
#                        reply_markup=InlineKeyboardMarkup().add(
#                            InlineKeyboardButton(text='Опубликовать', callback_data='post'),
#                            InlineKeyboardButton(text='Редактировать', callback_data='edit_post')).add(
#                            InlineKeyboardButton(text='Добавить фото', callback_data='add_photo')).add(
#                            InlineKeyboardButton(text='Главное меню', callback_data='main_menu'))
#                        )

def get_text(message):
    try:
        message.text.lower()
    except Exception as ex:
        print(ex)
        bot.send_message(message.chat.id, '<b>Вы прислали не текст, попробуйте еще раз!</b>', parse_mode='HTML',
                         reply_markup=ReplyKeyboardRemove())
        return bot.send_message(message.chat.id, '========== Главное-меню ==========', reply_markup=main_keyboard)

    if message.text.lower() != 'отменить':
        bot.delete_message(message.chat.id, message.message_id - 1)
        bot.delete_message(message.chat.id, message.message_id)

        # bot.send_message(message.chat.id, '======== ОБЪЯВЛЕНИЕ ========', reply_markup=ReplyKeyboardRemove())
        bot.send_message(message.chat.id, '<b>❗️НОВЫЙ ТЕКСТ ОБЪЯВЛЕНИЯ❗️</b>', parse_mode='HTML')
        bot.send_message(message.chat.id, message.text,
                         reply_markup=InlineKeyboardMarkup().add(
                             InlineKeyboardButton(text='Опубликовать', callback_data='post'),
                             InlineKeyboardButton(text='Редактировать текст', callback_data='edit_post')).add(
                             InlineKeyboardButton(text='Добавить фото', callback_data='add_photo')).add(
                             InlineKeyboardButton(text='Главное меню', callback_data='main_menu'))
                         )

    else:
        bot.delete_message(message.chat.id, message.message_id - 1)

        bot.send_message(message.chat.id, 'Действие отменено', reply_markup=ReplyKeyboardRemove())
        bot.send_message(message.chat.id, '========== Главное-меню ==========', reply_markup=main_keyboard)


def get_new_price(message):
    global price
    if message.text == 'Отменить':
        bot.send_message(message.chat.id, 'Действие отменено', reply_markup=ReplyKeyboardRemove())
    else:
        try:
            new_price = int(message.text)
        except ValueError:
            return bot.send_message(message.chat.id, 'Вы ввели не число, попробуйте еще раз',
                                    reply_markup=ReplyKeyboardRemove())

        price = new_price
        with sqlite3.connect(db_path) as con:
            cursor = con.cursor()
            cursor.execute('UPDATE info SET price = (?)', (new_price,))

        bot.send_message(message.chat.id, f'<b>Новая цена</b>: {price}₽', parse_mode='HTML',
                         reply_markup=ReplyKeyboardRemove())


def get_bonus_id(message):
    if message.text == 'Отменить':
        return bot.send_message(message.chat.id, 'Действие отменено', reply_markup=ReplyKeyboardRemove())

    try:
        id = int(message.text)
    except ValueError:
        return bot.send_message(message.chat.id, 'Вы ввели не id, попробуйте заново',
                                reply_markup=ReplyKeyboardRemove())

    bot.send_message(message.chat.id, f'[Пользователь](tg://user?id={id})', parse_mode='MarkdownV2')
    bot.send_message(message.chat.id, 'Введите сумму бонуса пользователя',
                     reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Отменить')))
    bot.register_next_step_handler(message, get_bonus_amount, id=id)


def get_bonus_amount(message, **kwargs):
    if message.text == 'Отменить':
        return bot.send_message(message.chat.id, 'Действие отменено', reply_markup=ReplyKeyboardRemove())

    try:
        amount = int(message.text)
    except ValueError:
        return bot.send_message(message.chat.id, 'Вы ввели не число, попробуйте заново',
                                reply_markup=ReplyKeyboardRemove())

    try:
        add_money(kwargs['id'], amount)
        bot.send_message(message.chat.id, f'Пользователю зачислилось {amount} рублей',
                         reply_markup=ReplyKeyboardRemove())
    except:
        bot.send_message(message.chat.id, 'Такого пользователя нет в базе данных пользователей')


def get_mail_data(message):
    if message.content_type == 'text':
        m = bot.send_message(message.chat.id, 'Подтвердите текст для рассылки')
        bot.send_message(message.chat.id, message.text, reply_to_message_id=m.message_id,
                         reply_markup=confirm_mail_keyboard)
        bot.register_next_step_handler(message, mail, data_type='text', mail_text=message.text)
    elif message.content_type == 'photo':
        if message.caption:
            m = bot.send_message(message.chat.id, 'Подтвердите фото для рассылки')
            bot.send_photo(message.chat.id, message.photo[0].file_id, caption=message.caption,
                           reply_to_message_id=m.message_id, reply_markup=confirm_mail_keyboard)
            bot.register_next_step_handler(message, mail, data_type='photo', mail_photo_id=message.photo[0].file_id,
                                           mail_caption=message.caption)
        else:
            m = bot.send_message(message.chat.id, 'Подтвердите фото для рассылки')
            bot.send_photo(message.chat.id, message.photo[0].file_id, reply_to_message_id=m.message_id,
                           reply_markup=confirm_mail_keyboard)
            bot.register_next_step_handler(message, mail, data_type='photo', mail_photo_id=message.photo[0].file_id, )

    elif message.content_type == 'video':
        if message.caption:
            m = bot.send_message(message.chat.id, 'Подтвердите видео для рассылки')
            bot.send_video(message.chat.id, message.video.file_id, caption=message.caption,
                           reply_to_message_id=m.message_id,
                           reply_markup=confirm_mail_keyboard)
            bot.register_next_step_handler(message, mail, data_type='video', mail_video_id=message.video.file_id,
                                           mail_caption=message.caption)
        else:
            m = bot.send_message(message.chat.id, 'Подтвердите видео для рассылки')
            bot.send_video(message.chat.id, message.video.file_id, reply_to_message_id=m.message_id,
                           reply_markup=confirm_mail_keyboard)
            bot.register_next_step_handler(message, mail, data_type='video', mail_video_id=message.video.file_id)
    else:
        bot.send_message(message.chat.id, 'Я не могу сделать рассылку этого файла')


def mail(message, **kwargs):
    if message.text.lower() == 'верно':
        try:
            with sqlite3.connect('data.db') as con:
                cursor = con.cursor()
                users = cursor.execute('SELECT user_id FROM users').fetchall()
        except Exception as ex:
            print(ex)
            return bot.send_message(message.chat.id, 'Не удалось получить список пользователей')
        bot.send_message(message.chat.id, 'Рассылка началась', reply_markup=ReplyKeyboardRemove())
        if kwargs['data_type'] == 'text':
            for i in users:
                try:
                    bot.send_message(i[0], kwargs['mail_text'])
                except:
                    pass

        elif kwargs['data_type'] == 'photo':
            try:
                caption = kwargs['mail_caption']
                for i in users:
                    try:
                        bot.send_photo(i[0], kwargs['mail_photo_id'], caption=caption)
                    except:
                        pass
            except:
                for i in users:
                    try:
                        bot.send_photo(i[0], kwargs['mail_photo_id'])
                    except:
                        pass

        elif kwargs['data_type'] == 'video':
            try:
                caption = kwargs['mail_caption']
                for i in users:
                    try:
                        bot.send_video(i[0], kwargs['mail_video_id'], caption=caption)
                    except:
                        pass
            except:
                for i in users:
                    try:
                        bot.send_video(i[0], kwargs['mail_video_id'])
                    except:
                        pass
        bot.send_message(message.chat.id, 'Рассылка окончена')

    else:
        bot.send_message(message.chat.id, 'Рассылка отменена', reply_markup=ReplyKeyboardRemove())


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except:
        print("Error")