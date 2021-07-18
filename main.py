import telebot as tl
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import time

conn = sqlite3.connect("D:/Promo_Bot/codes.db", check_same_thread=False)
cur = conn.cursor()
bot = tl.TeleBot("1875698946:AAF8fuerhwbxLpn9c8oPt4X3wG6bCaKITpY")

admin = [564039295]

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    id = call.message.caption[4:len(call.message.caption)]
    cur.execute("SELECT * FROM main WHERE id=?", (int(id),))
    if call.data == 'yes':
        cur.execute("UPDATE main SET status=? WHERE id=?", ('accepting', int(id)))
    if call.data == 'no':
        cur.execute("UPDATE main SET status=? WHERE id=?", ('rejecting', int(id)))
    conn.commit()

@bot.message_handler(content_types=['photo'])
def photo(message):
    cur.execute("SELECT * FROM main WHERE id=?", (message.caption,))
    if message.caption != None:
        if message.caption.isnumeric() and len(message.caption) == 7:
            if cur.fetchall() == []:
                bot.reply_to(message, "Запрос отправлен на модерацию")
                cur.execute("INSERT INTO main VALUES (?, ?, ?, ?, ?)", (str(message.caption), str(message.chat.id), 'waiting', str(message.photo[0].file_id), ''))
                conn.commit()
            else:
                bot.reply_to(message, "Этот код чека уже зарегестрирован")
        else:
            bot.reply_to(message, "Недействительный код чека")
    else:
        bot.reply_to(message, "Отправте номер на чеке и фото одним сообщениеы")

@bot.message_handler(commands=['start_for_all'])
def check(message):
    while True:
        time.sleep(10)
        cur.execute("SELECT * FROM main WHERE status='accepting'")
        for row in cur.fetchall():
            bot.send_message(int(row[1]), "Чек с кодом " + str(row[0]) + " был подтверждён")
            cur.execute("UPDATE main SET status='accepted' WHERE id=?", (row[0],))

        cur.execute("SELECT * FROM main WHERE status='rejecting'")
        for row in cur.fetchall():
            bot.send_message(int(row[1]), "Чек с кодом " + str(row[0]) + " был отклонён")
            cur.execute("UPDATE main SET status='rejected' WHERE id=?", (row[0],))
        conn.commit()

        cur.execute("SELECT * FROM main WHERE status='waiting'")
        for row in cur.fetchall():
            for us in admin:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("Принять", callback_data='yes'), InlineKeyboardButton("Отклонить", callback_data='no'))
                mes = bot.send_photo(us, row[3], caption="Код:" + str(row[0]), reply_markup=markup)
                cur.execute("UPDATE main SET mes=? WHERE id=?", ("," + row[4] + str(mes.message_id) + "," + str(mes.chat.id), row[0]))
        cur.execute("UPDATE main SET status='wait' WHERE status='waiting'")
        conn.commit()

        cur.execute("SELECT * FROM main WHERE status='accepted'")
        for row in cur.fetchall():
            listrow1 = row[4][1:].split(",")
            listrow = []
            for i in range(len(listrow1) // 2):
                listrow.append([listrow1[i * 2], listrow1[i * 2 + 1]])
            for us in listrow:
                bot.delete_message(us[1], us[0])
        cur.execute("UPDATE main SET status='accepted_del' WHERE status='accepted'")
        conn.commit()
        cur.execute("SELECT * FROM main WHERE status='rejected'")
        for row in cur.fetchall():
            listrow1 = row[4][1:].split(",")
            listrow = []
            for i in range(len(listrow1) // 2):
                listrow.append([listrow1[i * 2], listrow1[i * 2 + 1]])
            for us in listrow:
                bot.delete_message(us[1], us[0])
        cur.execute("UPDATE main SET status='rejected_del' WHERE status='rejected'")
        conn.commit()       

@bot.message_handler(commands=['start'])
def start(message):
	bot.reply_to(message, "Привет")

@bot.message_handler()
def no(message):
    bot.reply_to(message, "Отправте номер на чеке и фото одним сообщение")

bot.polling()