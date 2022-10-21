from flask import Flask, request
import requests
from config import TOKEN, URL, file_unique_id, file_id
import json
import hashlib
import sqlite3 as sq


shop = 1
amount = 1273.0
desc = 'Тестовый'
secret = 'jhewfhhujh'
currency = 'RUB'
keyboard = ['GG', "Привет"]


#https://api.telegram.org/bot1907550104:AAHSfjA7bX9xVSfAZp9Kk_1mKEaQZq_P52c/setwebhook?url=https://2668-37-215-35-122.eu.ngrok.io?secret_token=1907550104:AAHSfjA7bX9xVSfAZp9Kk_1mKEaQZq_P52c
#https://api.telegram.org/bot5690838149:AAHPNDSyHfjLfo65TbO71m1LI55OCrBTmww/setwebhook?url=https://6758-37-215-35-122.eu.ngrok.io?secret_token=5690838149:AAHPNDSyHfjLfo65TbO71m1LI55OCrBTmww
app = Flask(__name__)

def sql_start():
	global cur_state, base_state
	base_state = sq.connect('izolde3.db', check_same_thread=False)
	cur_state = base_state.cursor()
	base_state.execute('CREATE TABLE IF NOT EXISTS user_state(username PRIMARY KEY, state)')
	base_state.commit()
sql_start()

def set_webhook(bot_id,URL):
	method = 'setWebhook'
	url = f'https://api.telegram.org/bot{bot_id}/setwebhook?url={URL}?secret_token={bot_id}'
	return requests.get(url).json()['ok']
	

set_webhook(bot_id = TOKEN,URL =URL)

def send_message(bot_id,chat_id, text ):
	method = 'sendMessage'
	url = f'https://api.telegram.org/bot{bot_id}/{method}'
	data = {'chat_id':chat_id,'text':text}
	requests.post(url,data=data)

def send_document(bot_id,chat_id):
	method = 'sendDocument'
	url = f'https://api.telegram.org/bot{bot_id}/{method}'
	data = {'chat_id':chat_id,'document':file_id}
	requests.post(url,data=data)

def send_inline_keyboard(bot_id, chat_id, text, but_text,send_url ):
	method = 'sendMessage'
	url = f'https://api.telegram.org/bot{bot_id}/{method}'
	data = {'chat_id':chat_id, 'text':text, 'reply_markup': json.dumps({'inline_keyboard':[[{'text':but_text,'url':send_url}]]})}
	requests.post(url,data=data)

def send_keyboard(bot_id, chat_id, text ):
	method = 'sendMessage'
	url = f'https://api.telegram.org/bot{bot_id}/{method}'
	data = {'chat_id':chat_id, 'text':text, 'reply_markup': json.dumps({'keyboard':[[{'text':'Статистика'},{'text':'Подключить'},{'text':'Баланс'}]],'resize_keyboard':True})}
	requests.post(url,data=data)

def send_keyboard_menu(bot_id, chat_id, text ):
	method = 'sendMessage'
	url = f'https://api.telegram.org/bot{bot_id}/{method}'
	data = {'chat_id':chat_id, 'text':text, 'reply_markup': json.dumps({'keyboard':[[{'text':'Меню'}]],'resize_keyboard':True})}
	requests.post(url,data=data)

def send_keyboard_withdraw(bot_id, chat_id, text ):
	method = 'sendMessage'
	url = f'https://api.telegram.org/bot{bot_id}/{method}'
	data = {'chat_id':chat_id, 'text':text, 'reply_markup': json.dumps({'keyboard':[[{'text':'Запросить вывод'},{'text':'Меню'}]],'resize_keyboard':True})}
	requests.post(url,data=data)

def send_keyboard_customer(bot_id, chat_id, text ):
	method = 'sendMessage'
	url = f'https://api.telegram.org/bot{bot_id}/{method}'
	data = {'chat_id':chat_id, 'text':text, 'reply_markup': json.dumps({'keyboard':[[{'text':'Купить программу'},{'text':'Как использовать'}]],'resize_keyboard':True})}
	requests.post(url,data=data)

def reg_message(bot_id,chat_id, message_text,first_name,date, message_id, username):
	if bot_id == TOKEN:
		state= cur_state.execute('SELECT state FROM user_state WHERE username==?',(username,)).fetchone()
		if message_text == '/start':
			send_keyboard(bot_id=bot_id, chat_id = chat_id, text = 'Привет '+ first_name+'!')
			cur_state.execute('INSERT or REPLACE INTO user_state VALUES(?,?)',(username, 'Меню'))
			base_state.commit()

		elif  message_text == 'Подключить':
			send_keyboard_menu(bot_id=bot_id, chat_id = chat_id, text = 'Введите ключ бота')
			
			cur_state.execute('INSERT or REPLACE INTO user_state VALUES(?,?)',(username, 'Подключить'))
			base_state.commit()

		elif message_text == 'Баланс':
			send_keyboard_withdraw(bot_id=bot_id, chat_id = chat_id, text = 'Баланс пользователя')

		elif message_text == 'Запросить вывод':
			send_keyboard_menu(bot_id=bot_id, chat_id = chat_id, text = 'Введите сумму к выводу')
			
			cur_state.execute('INSERT or REPLACE INTO user_state VALUES(?,?)',(username, 'Запросить вывод'))
			base_state.commit()

		elif message_text == 'Меню':
			send_keyboard(bot_id=bot_id, chat_id = chat_id, text = 'Меню')
			cur_state.execute('INSERT or REPLACE INTO user_state VALUES(?,?)',(username, 'Меню'))
			base_state.commit()
		else:
			if state[0] =='Подключить' :
				if set_webhook(bot_id = message_text,URL=URL) == True:
					send_keyboard(bot_id=bot_id, chat_id = chat_id, text = 'Бот успешно подключен')
					cur_state.execute('INSERT or REPLACE INTO user_state VALUES(?,?)',(username, 'Меню'))
					base_state.commit()
				else:
					send_keyboard_menu(bot_id=bot_id, chat_id = chat_id, text = 'Некорректный токен бота')

			if state[0] =='Запросить вывод' :
				send_keyboard(bot_id=bot_id, chat_id = chat_id, text = 'К выводу '+message_text+' USDT')
				cur_state.execute('INSERT or REPLACE INTO user_state VALUES(?,?)',(username, 'Меню'))
				base_state.commit()

	else:
		if message_text == '/start':
			send_keyboard_customer(bot_id=bot_id, chat_id = chat_id, text = 'Привет '+ first_name+'!')
			send_message(bot_id=bot_id, chat_id = chat_id, text = 'Описание софта')
		elif message_text== 'Купить программу':
			send_inline_keyboard(bot_id=bot_id, chat_id = chat_id, text = 'Чек',but_text='Купить', send_url='https://music.youtube.com/watch?v=HnDyj287iKw')
		elif message_text== 'Как использовать':
			send_inline_keyboard(bot_id=bot_id, chat_id = chat_id, text = 'Гайд',but_text='Читать', send_url='https://music.youtube.com/watch?v=9iCoK6PaKQI')

@app.route('/', methods=['POST'])
def process():
	chat_id = request.json['message']['chat']['id']
	first_name = request.json['message']['from']['first_name']
	username = request.json['message']['from']['username']
	date = request.json['message']['date']
	message_id = request.json['message']['message_id']
	message_text = request.json['message']['text']
	bot_id = (request.url[-46:])
	#send_document(bot_id=bot_id,chat_id=chat_id)
	reg_message(bot_id = bot_id, chat_id = chat_id, message_text = message_text, first_name = first_name, date = date,message_id = message_id,username = username)
	return{'ok': True}



if __name__ == '__main__':
	app.run()