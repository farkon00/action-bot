import telebot as tl
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import time

conn = sqlite3.connect("D:/Promo_Bot/codes.db", check_same_thread=False)
cur = conn.cursor()
bot = tl.TeleBot("1830481163:AAH3CW5jB4fYvdzEHj0fYzc67NzjGV2Te48")

admin = [564039295]

@bot.message_handler(commands=['start_for_all1'])
def check1(message):
    mes_id = 3
    while True:
        time.sleep(1)
        print(mes_id, "not try")
        try:
            if message.media_group_id == "photo":
                mes_id += 1
                print(mes_id)
                for us in admin:
                    mes = bot.forward_message(us, -506463288, mes_id)
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton("Принять", callback_data='yes'), InlineKeyboardButton("Отклонить", callback_data='no'))
                    ch = bot.reply_to(mes, "Ваш выбор:", reply_markup=markup)

                    cur.execute("SELECT * FROM main WHERE id=?", (mes.caption,))
                    row = cur.fetcall()
                    cur.execute("UPDATE main SET mes=? WHERE id=?", (str(list(row[3]) + [mes.message_id, ch.message_id, mes.chat.id]), mes.caption))
        except:
            mes_id = mes_id


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
        id = call.message.caption[4:len(call.message.caption)]
        cur.execute("SELECT * FROM main WHERE id=?", (int(id),))
        if call.data == 'yes':
            cur.execute("UPDATE main SET status=? WHERE id=?", ('accepting', id))
        if call.data == 'no':
            cur.execute("UPDATE main SET status=? WHERE id=?", ('rejecting', id))
        conn.commit()

@bot.message_handler(commands=['start_for_all'])
def check(message):
    while True:
        time.sleep(10)
        cur.execute("SELECT * FROM main WHERE status='waiting'")
        for row in cur.fetchall():
            for us in admin:
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("Принять", callback_data='yes'), InlineKeyboardButton("Отклонить", callback_data='no'))
                mes = bot.forward_message(us, row[1], row[3])
                ch = bot.reply_to(mes, "Ваш выбор:", reply_markup=markup)
                cur.execute("UPDATE main SET mes=? WHERE id=?", (str(list(row[3]) + [mes.message_id, ch.message_id, mes.chat.id]), row[0]))
        cur.execute("UPDATE main SET status='wait' WHERE status='waiting'")
        conn.commit()

bot.polling()