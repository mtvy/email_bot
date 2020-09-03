import schedule
import datetime
import psycopg2
import telebot
import imaplib
import config
import email
import time
import json
import sys
import io
import os
from multiprocessing import *
from telebot import types



#with open(path_acc_settings, 'r') as file_set:
#   if(file_set.readline() == ""): account_settings = {}
#    else:
#        file_set.close()
#        with open(path_acc_settings, 'r') as file_set:
#            account_settings = json.load(file_set)

bot = telebot.TeleBot(config.TOKEN)

def connect():
    try:
        con = psycopg2.connect(database="postgres",user="postgres",password="14072003", host="127.0.0.1",port="5432")
        cur = con.cursor()
        return con, cur
    except (Exception, psycopg2.DatabaseError) as error:
        print ("Error while connecting PostgreSQL!", error)
        return 0

def checkPersonInDataBase(message):
    con, cur = connect()
    if con == 0 and cur == 0:
        return 0
    else:
        try:
            txt_db_com = "SELECT tg_id FROM user_tb"
            cur.execute(txt_db_com)
            ed_text = cur.fetchall()
            for ids in ed_text:
                if str(ids[0]) == str(message.chat.id):
                    con.commit()
                    return 1
            con.commit()
            return 0
        except Exception as error:
            print('Error taking tg_id!', error)
            return 0

def checkEmailInDataBase(message):
    con, cur = connect()
    if con == 0 and cur == 0:
        return 0
    else:
        try:
            txt_db_com = "SELECT email FROM user_tb WHERE tg_id = '" + str(message.chat.id) + "'"
            cur.execute(txt_db_com)
            ed_text = cur.fetchall()
            con.commit()
            return ed_text[0][0]
        except Exception as error:
            print('Error taking email from database!', error)
            return 0

def activateAccount(message):
    con, cur = connect()
    if con == 0 and cur == 0:
        return 0
    else:
        try:
            txt_db_com = "UPDATE user_tb SET activation = 'YES' WHERE activation = 'NO' AND tg_id = '" + str(message.chat.id) + "'"
            cur.execute(txt_db_com)
            con.commit()
            print('Bot was activated by user ' + str(message.chat.id) + '!')
            return 1
        except Exception as error:
            print('Error updating activation status!', error)
            return 0

def takeEmailFromDataBase():
    con, cur = connect()
    if con == 0 and cur == 0:
        return 0
    else:
        try:
            txt_db_com = "SELECT email, password, tg_id FROM user_tb WHERE activation = 'YES'"
            cur.execute(txt_db_com)
            email_and_password = cur.fetchall()
            con.commit()
            return email_and_password
        except Exception as error:
            print('Error taking email from database!', error)
            return 0

def addNewPersonIdToDataBase(message):
    con, cur = connect()
    if con == 0 and cur == 0:
        bot.send_message(message.chat.id, 'Ошибка в добалении почты! Попробуйте заново или обратитесь к оператору!')
        return 0
    else:
        try:
            txt_db_com = "INSERT INTO user_tb (tg_id, last_email_id, activation) VALUES ('" + message.text + "', 'b''0''', 'W')"
            cur.execute(txt_db_com)
            con.commit()
        except Exception as error:
            bot.send_message(message.chat.id, 'Id не добавлен попробуйте позже!')
            print('Error entering new id to user_tb!', error)
            return 0
        send = bot.send_message(message.chat.id, 'Введите email пользователя (login@email.com)')
        bot.register_next_step_handler(send, addNewPersonEmailToDataBase)
def addNewPersonEmailToDataBase(message):
    con, cur = connect()
    if con == 0 and cur == 0:
        bot.send_message(message.chat.id, 'Ошибка в добалении почты! Попробуйте заново или обратитесь к оператору!')
        return 0
    else:
        try:
            txt_db_com = "UPDATE user_tb SET email = '" + message.text + "' WHERE activation = 'W'"
            cur.execute(txt_db_com)
            con.commit()
        except Exception as error:
            bot.send_message(message.chat.id, 'email не добавлен попробуйте позже!')
            print('Error entering new email to user_tb!', error)
            return 0
        send = bot.send_message(message.chat.id, 'Введите password пользователя (asdasd1231233)')
        bot.register_next_step_handler(send, addNewPersonPasswordToDataBase)
def addNewPersonPasswordToDataBase(message):
    con, cur = connect()
    if con == 0 and cur == 0:
        bot.send_message(message.chat.id, 'Ошибка в добалении почты! Попробуйте заново или обратитесь к оператору!')
        return 0
    else:
        try:
            txt_db_com = "UPDATE user_tb SET password = '" + message.text + "', activation = 'NO' WHERE activation = 'W'"
            cur.execute(txt_db_com)
            con.commit()
            bot.send_message(message.chat.id, 'Пользователь добавлен для рассылки!')
        except Exception as error:
            bot.send_message(message.chat.id, 'Ошибка в добалении почты! Попробуйте заново или обратитесь к оператору!')
            txt_db_com = "DELETE FROM user_tb WHERE activation = 'W'"
            cur.execute(txt_db_com)
            con.commit()
            print('Error entering new email to user_tb!', error)
            return 0

def deletePersonFromDataBase(message):
    con, cur = connect()
    if con == 0 and cur == 0:
        bot.send_message(message.chat.id, 'Ошибка в чтении почты! Попробуйте заново или обратитесь к оператору!')
        return 0
    else:
        try:
            txt_db_com = "DELETE FROM user_tb WHERE tg_id = '" + message.text + "'"
            cur.execute(txt_db_com)
            con.commit()
            bot.send_message(message.chat.id, 'Пользователь удалён из БД!')
        except Exception as error:
            bot.send_message(message.chat.id, 'Ошибка в чтении почты! Попробуйте заново или обратитесь к оператору!')
            print('Error deleting email from user_tb!', error)
            return 0

def insert_new_data(user_id, oper_id):
    con, cur = connect()
    if con == 0 and cur == 0:
        return 0
    else:
        try:
            if oper_id == '0':
                dt = datetime.date.today()
                tt = dt.timetuple()
                date_start = ''
                ch_i = 0
                for it in tt:
                    date_start += str(it)
                    ch_i += 1
                    if ch_i >= 3: break
                    else: date_start += '-'
                txt_db_com = "INSERT INTO message_tb (user_id, oper_id, date_start, text, status) VALUES (" + user_id + ', ' + oper_id + ", '" + date_start + "', 'TEXT DATABASE', 'open')"
                cur.execute(txt_db_com)
                con.commit()
                print('New data add!')
                return 1
            elif user_id != '0' and oper_id != '0':
                txt_db_com = "UPDATE message_tb SET oper_id = " + oper_id + ", text = '" + "TEXT DATABASE\nOperator: " + oper_id + "\nUser: " + user_id + "\n'" + " WHERE status = 'open' AND user_id = " + user_id
                cur.execute(txt_db_com)
                con.commit()
                print('New data add!')
                txt_db_com = "SELECT id FROM message_tb WHERE status = 'open' and user_id = " + user_id
                cur.execute(txt_db_com)
                ed_text = cur.fetchall()
                text_adder = ed_text[0]
                text_adder = '✏️id Переписки: ' + str(text_adder[0])
                bot.send_message(int(oper_id), text_adder)
                bot.send_message(int(user_id), text_adder)
                return 1
        except Exception as error:
            print('Error entering new data to message_tb!', error)
            return 0

def insert_text_to_data(text_val, sm_id):
    con, cur = connect()
    if con == 0 and cur == 0:
        return 0
    else:
        try:
            txt_db_com = "SELECT text FROM message_tb WHERE status = 'open' and (oper_id = " + sm_id + ' or user_id = ' + sm_id + ')'
            cur.execute(txt_db_com)
            ed_text = cur.fetchall() 
            text_adder = ed_text[0]
            text_adder = text_adder[0] + '\n' + text_val
            txt_db_com = "UPDATE message_tb SET text = '" + text_adder + "' WHERE status = 'open' and (user_id = " + sm_id + ' or oper_id = ' + sm_id + ')'
            cur.execute(txt_db_com)
            con.commit()
            return 1
        except Exception as e:
            print('Error entering data to message_tb!', e)
            return 0

def closerDataBase(sm_id):
    con, cur = connect()
    if con == 0 and cur == 0:
        return 0
    else:
        try:
            txt_db_com = "SELECT user_id, oper_id FROM message_tb WHERE status = 'open' and (oper_id = " + sm_id + ' or user_id = ' + sm_id + ')'
            cur.execute(txt_db_com)
            ed_text = cur.fetchall()
            if ed_text[0][0] == 0 or ed_text[0][1] == 0:
                txt_db_com = "delete from message_tb where status = 'open' and (oper_id = " + sm_id + ' or user_id = ' + sm_id + ')'
                cur.execute(txt_db_com)
            else:
                txt_db_com = "UPDATE message_tb SET status = 'close' WHERE status = 'open' and user_id = " + sm_id + ' or oper_id = ' + sm_id
                cur.execute(txt_db_com)
            con.commit()
            return 1
        except Exception as e:
            print('Error entering data to message_tb!', e)
            return 0

def getDataFromDB(date_start):
    con, cur = connect()
    if con == 0 and cur == 0:
        return 0
    else:
        try:
            txt_db_com = "SELECT id, user_id FROM message_tb WHERE date_start = '" + date_start + "'"
            cur.execute(txt_db_com)
            ed_text = cur.fetchall()
            text_adder = 'ID ПОЛЬЗОВАТЕЛЕЙ\n\n'
            #for i in ed_text:
            #    for k in account_settings:
            #        if k == str(i[1]):
            #            if account_settings[k]['login'] != 'None':
            #                name_id = '@' + account_settings[k]['login']
            #            else: name_id = account_settings[k]['name']
            #            break
            #    text_adder = text_adder + str(i[0]) + ') ' + 'Name: ' + name_id + ' --- Id: ' + str(i[1]) + '\n'
            con.commit()
            if text_adder == 'ID ПОЛЬЗОВАТЕЛЕЙ\n\n': return '0' 
            else: return text_adder
        except Exception as e:
            print('Error data message_tb!', e)
            return '0'

def getTextFromDB(id_text):
    con, cur = connect()
    if con == 0 and cur == 0:
        return 0
    else:
        try:
            txt_db_com = "SELECT text FROM message_tb WHERE id = " + id_text
            cur.execute(txt_db_com)
            ed_text = cur.fetchall()
            text_taker = ed_text[0]
            text_taker = text_taker[0]
            con.commit()
            return text_taker
        except Exception as e:
            print('Error, wrong id!', e)
            return '0'

def change_data(name):
    con, cur = connect()
    if con == 0 or cur == 0:
        return 0
    else:
        try:
            txt_data_del = "UPDATE user_tb set phone = NULL where name = '" + name + "'"
            cur.execute(txt_data_del)  
            con.commit()   
        except Exception as e:
            err_txt = 'Error deleting data from user @' + name + '!'
            print(err_txt, e)


def start_process():
    p1 = Process(target=P_schedule.start_schedule, args=()).start()
class P_schedule():
    def start_schedule():
        schedule.every(1).seconds.do(P_schedule.send_post)
        
        while True:
            schedule.run_pending()
            time.sleep(1)
    def send_post():
        email_db = takeEmailFromDataBase()
        for it in email_db:
            mailSet(it[0], it[1], it[2])

def takeLastEmailId(last_id, person_id, user):
    con, cur = connect()
    if con == 0 and cur == 0:
        return 0
    else:
        try:
            txt_db_com = "SELECT last_email_id FROM user_tb WHERE tg_id = '" + person_id + "' and email = '" + user + "'"
            cur.execute(txt_db_com)
            ed_text = cur.fetchall()
            last_id = str(last_id)
            if ed_text != None and ed_text[0][0][2:-1] < last_id[2:-1]:
                txt_db_com = "UPDATE user_tb SET last_email_id = 'b''" + last_id[2:-1] + "''' WHERE tg_id = '" + person_id + "' and email = '" + user + "'"
                cur.execute(txt_db_com)
                con.commit()
                return 1
            else:
                con.commit()
                return 0
        except Exception as e:
            print('Error changing last_email_id in database!', e)
            return 0

def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

def mailSet(user, password, person_id):
    user ='testt@mail.analizy.uz'
    password ='~a5#53)OHQ}SwlX=xY5tgty76bnje4cmh'
    imap_url ='mail.analizy.uz'
    con = imaplib.IMAP4_SSL(imap_url)
    con.login(user,password)
    con.select('INBOX')
    result, data = con.search(None, "ALL")
    id_list = data[0].split()
    latest_email_id = id_list[-1]
    check_last_email_id = takeLastEmailId(latest_email_id, person_id, user)
    if check_last_email_id != 1: return
    result, data = con.fetch(latest_email_id, ' (RFC822) ')
    raw = email.message_from_bytes(data[0][1])
    show_bottom = email.utils.parseaddr(raw['From'])
    email_body_text = get_body(raw).decode("utf-8")
    check_ln = 0
    contents = []
    name_cont = []
    for part in raw.walk():
        #print(part.get_content_type())
        if part.get_content_type() == 'application/pdf':     
                payload = part.get_payload(decode=True)
                filename = part.get_filename()
                if payload and filename:
                    with open(filename, 'wb') as f:
                        f.write(payload)
                        f.close()
                    with open(filename, 'rb') as f:
                        contents.append(f.read())
                        name_cont.append(filename)
                        #print('File was saved!')
                    check_ln = 1
                    #bot.send_photo(int(person_id), contents)
                    os.remove(filename)
    bot.send_message(int(person_id), '🔔 Email получен от ' + show_bottom[1] + '\n🔔 Username: ' + show_bottom[0] + '\n\n' + email_body_text)
    if check_ln != 0:
        for i in range(len(contents)):
            bot.send_document(int(person_id),contents[i], caption = 'Файл №' + str(i + 1) + '\nНазвание файла: ' + name_cont[i])



@bot.message_handler(commands=['start'])
def welcome(message):
    if message.chat.id == 281321076 or message.chat.id == 667068180:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("➕ Добавить в БД")
        item2 = types.KeyboardButton("➖ Удалить из БД")
        markup.add(item1, item2)
        bot.send_message(message.chat.id, 'У вас права администратора!', reply_markup=markup)
    id_checker = checkPersonInDataBase(message)
    if id_checker == 1:
        if message.from_user.username != None: name_pers = message.from_user.username
        elif message.from_user.first_name != None: name_pers = message.from_user.first_name
        else: name_pers = 'гость'
        bot.send_message(message.chat.id, '📩 Добро пожаловать в бот по обработке почты, ' + name_pers + '!\n📩 Новые письма будут автоматический отправлятся в переписку с ботом.')
        email_taker = checkEmailInDataBase(message)
        if email_taker != None: 
            bot.send_message(message.chat.id, 'Ваш email: ' + email_taker)
            activateAccount(message)
        else: 
            bot.send_message(message.chat.id, 'Вашего email нет в базе данных, обратитесь к оператору!')
            return
    else: bot.send_message(message.chat.id, 'Вас нет в базе данных, обратитесь к оператору!')



@bot.message_handler(content_types=['text', 'photo'])
def lol(message):
    if message.chat.type == 'private':
        if message.text == '➕ Добавить в БД':
            send = bot.send_message(message.chat.id, 'Введите id пользователя (2353252)')
            bot.register_next_step_handler(send, addNewPersonIdToDataBase)
        elif message.text == '➖ Удалить из БД':
            send = bot.send_message(message.chat.id, 'Введите id пользователя для удаления (2353252)')
            bot.register_next_step_handler(send, deletePersonFromDataBase)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global new_acc_id
    global account_settings
    global mess
    try:
        if call.data == 'Русский':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            new_acc_id = ""
            markup = types.InlineKeyboardMarkup(row_width=2)
            item1 = types.InlineKeyboardButton("Согласен", callback_data='Согласен')
            item2 = types.InlineKeyboardButton("Отказываюсь", callback_data='Отказываюсь')
            markup.add(item1, item2)
       
    except Exception as e:
        print(repr(e))
        
#RUN
if __name__ == '__main__':
    start_process()
    try:
        bot.polling(none_stop=True)
    except:
        pass
