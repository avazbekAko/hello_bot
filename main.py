import telebot

import time

from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

BOT_TOKEN = '5190238051:AAEPFIc1NmGfY2uS7eheO0G5plWEzG_r2WM'

bot = telebot.TeleBot(BOT_TOKEN)

admin_ids = [1894088037]


text_EN = '''Free registration 
💰$12 signup bonus
🔝Top Up your balance from 100 USDT, get bonuses, rewards and 💵earn a lot of money💰
👫‍100 people register and top up the balance daily
💸Сryptocurrency - USDT TRC-20
💵 For 100 USDT gives 3 USDT daily
💵 For 300 USDT gives 10 USDT daily
💵 For 500 USDT gives 20 USDT daily
💵 For 750 USDT gives 25 USDT daily
💵 For 1000 USDT gives 30 USDT daily
💰💰 Invitation Rewards
👫 Invite a friend on the same day to sign up and recharge 100  USDT, get a 5  USDT to your Binance BONUS
👫 Invite a friend on the same day to sign up and recharge 500  USDT, get a 10 USDT to your Binance BONUS
👫 Invite a friend on the same day to sign up and recharge 1000 USDT, get a 20 USDT to your Binance BONUS
⬇️Link to the game⬇️
https://h5.otw60.com/#/?code=SJG42B
'''


text_RU_EN = '''Бесплатная регистрация
💰$12 бонус за регистрацию
🔝Пополняйте баланс от 100 USDT, получайте бонусы, вознаграждения и 💵зарабатывайте много денег💰
👫‍100 человек регистрируются и пополняют баланс ежедневно
💸Криптовалюта - USDT TRC-20
💵 За 50 USDT дает 1,5 USDT в день
💵 За 100 USDT дают 3 USDT в день
💵 За 300 USDT дает 10 USDT ежедневно
💵 За 500 USDT дает 20 USDT ежедневно
💵 За 750 USDT дает 25 USDT ежедневно
💵 За 1000 USDT ежедневно дают 30 USDT
💰💰 Награды за приглашения
👫 Пригласите друга в тот же день, чтобы зарегистрироваться и пополнить 100 USDT, получите 5 USDT в свой БОНУС Binance
👫 Пригласите друга в тот же день, чтобы зарегистрироваться и пополнить 500 USDT, получите 10 USDT в свой БОНУС Binance.
👫 Пригласите друга в тот же день, чтобы зарегистрироваться и пополнить 1000 USDT, получите 20 USDT в свой БОНУС Binance.
⬇️Ссылка на игру⬇️
https://h5.otw60.com/#/?code=SJG42B

=========================

Free registration 
💰$12 signup bonus
🔝Top Up your balance from 100 USDT, get bonuses, rewards and 💵earn a lot of money💰
👫‍100 people register and top up the balance daily
💸Сryptocurrency - USDT TRC-20
💵 For 100 USDT gives 3 USDT daily
💵 For 300 USDT gives 10 USDT daily
💵 For 500 USDT gives 20 USDT daily
💵 For 750 USDT gives 25 USDT daily
💵 For 1000 USDT gives 30 USDT daily
💰💰 Invitation Rewards
👫 Invite a friend on the same day to sign up and recharge 100  USDT, get a 5  USDT to your Binance BONUS
👫 Invite a friend on the same day to sign up and recharge 500  USDT, get a 10 USDT to your Binance BONUS
👫 Invite a friend on the same day to sign up and recharge 1000 USDT, get a 20 USDT to your Binance BONUS
⬇️Link to the game⬇️
https://h5.otw60.com/#/?code=SJG42B
'''


Welcome_text = '''Welcome to group "On the way project"
🔝 Top Up your balance from 100 USDT, get bonuses, rewards and 💵earn a lot of money💰
😎 We are glad to you and wish good luck
'''

murkup_admin = InlineKeyboardMarkup().add(
	InlineKeyboardButton('Спамить текст 1', callback_data='txt_1'),
	InlineKeyboardButton('Спамить текст 2', callback_data='txt_2'),
	InlineKeyboardButton('Спамить текст 3', callback_data='txt_3')
	)

@bot.message_handler(content_types = ['new_chat_members'])
def user_joined(message):
	bot.send_message(message.chat.id, f"🖐 {message.json['new_chat_member']['first_name']} " + Welcome_text)
	bot.delete_message(message.chat.id, message.message_id)
	print("Hi delete")


@bot.message_handler(content_types = ['left_chat_member'])
def user_kik(message):
	bot.delete_message(message.chat.id, message.message_id)
	print("delete")


@bot.message_handler(commands=['admin'])
def admin(message):
	if message.chat.id in admin_ids:
		bot.send_message(message.chat.id, 'Админ Панель', reply_markup=murkup_admin)

@bot.message_handler(commands='test')
def admin(message):
	bot.send_message(message.chat.id, 'Hello')


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
	if call.message:
		if call.data == 'txt_1':
			while True:
				try:
					bot.send_message(-1001781819186, text_RU_EN)
					time.sleep(7200)
				except:
					time.sleep(1)

try:
	bot.polling(none_stop=True)
except:
	print("Error")