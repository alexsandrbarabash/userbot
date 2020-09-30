from pyrogram import Client, filters
import os
import const
import json
import sqlite3
'''
db=sqlite3.connect('server.db')
sql=db.cursor()
'''
app=Client('my_account')

# Прикол не звертати уваги кинь боту сірого чувака і він відповість
@app.on_message(filters.sticker)
def reply_sticker(_, message):
    me='gerach'# Перевірка щоб не тегало самого себе
    print(message)
    if(message.from_user.username!=me):
        if(message.sticker.file_id == const.STIKER_REPLY_RIGHT):
            file_id = open('left.webp', 'rb')
            app.send_sticker(message.chat.id, file_id, reply_to_message_id=message.message_id)

        if (message.sticker.file_id == const.STIKER_REPLY_LEFT):
            file_id = open('right.webp', 'rb')
            app.send_sticker(message.chat.id, file_id, reply_to_message_id=message.message_id)

# Тегнути всіх користувачів групи
@app.on_message(filters.command("all", prefixes=".") & filters.me & filters.group)
def teg_all(_,message):
    #print(message)
    user_id=[]
    for x in app.iter_chat_members(message.chat.id):
        user_id.append([x.user.id, x.user.first_name])

    all_members=""
    for item in user_id:
        all_members=all_members+f"<a href='tg://user?id={item[0]}'>{item[1]}</a> "

    app.send_message(message.chat.id, f"{all_members}", parse_mode='html')


#Перевірка повідомлень на повторення (реакції)

def create_db():
    db = sqlite3.connect('server.db')
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS badmems (
        fileid VARCHAR(40)
    )""")
    db.commit()

def cheack_mem(file_id):
    db = sqlite3.connect('server.db')
    cursor = db.cursor()
    create_db()
    cursor.execute("SELECT * FROM badmems WHERE fileid=?", (file_id,))
    result = cursor.fetchall()
    if result == []:
        return False
    else:
        return True
def add_new_badmems(file_id):
    db = sqlite3.connect('server.db')
    cursor = db.cursor()
    cursor.execute("INSERT INTO badmems VALUES (?)", (file_id,))
    db.commit()

# Оброник модератора і каналу для відправки
def update_data(what_update, id):
    try:
        with open('data.json') as f:
            data=json.load(f)
            data[what_update]=id#Додаємо id Модератора або чату для відправки

        with open('data.json', 'w') as f:
            json.dump(data, f)

    except:
        data = {'MODERATOR': '','CHENNEL_FOR_SEND_CONTENT':''}
        with open('data.json', 'w') as f:
            json.dump(data, f)

        return update_data(what_update,id)


# Отримання id Модератора з файла data
def get_id_moderator():
    f = open('data.json')
    data = json.load(f)
    f.close()
    return data['MODERATOR']

# Отримання id каналу куди переселати дані після пітверження модератором
def get_id_chennel_for_send_content():
    f = open('data.json')
    data = json.load(f)
    f.close()
    return data['CHENNEL_FOR_SEND_CONTENT']

# Перевірка на існування модератора і канала для відправки повідомлень
def data_is():
    try:
        with open('data.json') as f:
            data = json.load(f)
        if (data['MODERATOR'] == '' or data['CHENNEL_FOR_SEND_CONTENT'] == ''):
            return False
        else:
            return True
    except:
        return False

# Обробник типу мема
def send_media(where, message):
    if (message.photo):
        # скачуємо фото
        app.download_media(message, file_name='photo.jpg')
        # message.download(file_name='photo.jpg')
        file_id = open('downloads/photo.jpg', 'rb')

        if (message.caption):
            app.send_photo(where, file_id, caption=message.caption)  # відправляємо фото модературу з текстом
        else:
            app.send_photo(where, file_id)  # відправляємо фото модературу без тексту
        # видаляємо фотку
        os.remove("downloads/photo.jpg")
        file_id.close()

    elif(message.animation):
        # скачуємо гівку
        app.download_media(message, file_name='giv.mp4')

        file_id = open('downloads/giv.mp4', 'rb')

        app.send_animation(where , file_id)  # відправляємо гівку
        # видаляємо гівку
        os.remove("downloads/giv.mp4")
        file_id.close()

    elif (message.video and int(message.video.file_size)<20971520):#відемо не може бути більши 20МБ

        # скачуємо відео
        app.download_media(message, file_name='video.mp4')

        file_id = open('downloads/video.mp4', 'rb')
        if (message.caption):
            app.send_video(where, file_id, caption=message.caption)  # відправляємо відео модературу з текстом
        else:
            app.send_video(where, file_id)  # відправляємо відео модературу без тексту

        # видаляємо відео
        os.remove("downloads/video.mp4")
        file_id.close()


# Зміна модератора
# Може лише бот
@app.on_message(filters.command("newmoder", prefixes=".") & filters.me & filters.private)
def new_moder(_,message):
    #print(message.chat.id)
    update_data('MODERATOR',  str(message.chat.id))

# Зміна канала для відправки повідомлення
# Може лише бот (баг який треба пофіксити)
@app.on_message(filters.command("newchannel", prefixes=".") & filters.me)
def new_channel(_,message):
    #print(message.chat)
    update_data('CHENNEL_FOR_SEND_CONTENT',  str(message.chat.id))

# Парсем меми і відправляємо модератору
@app.on_message(filters.channel)
def parsing_chennel(_,message):
    #print('Send chennel')
    #print(message)
    # повідомлення з реакцією
    if(message.reply_markup):
        if (cheack_mem(message.photo.file_id)):
            return None
        else:
            if(message.text=='.newchannel'):
                update_data('CHENNEL_FOR_SEND_CONTENT', str(message.chat.id))
            if(data_is() and str(message.chat.id)!=get_id_chennel_for_send_content()):
                send_media(get_id_moderator(), message)#відправляємо мем модератору через обробник типу мема
            add_new_badmems(message.photo.file_id)
    else:
        if (message.text == '.newchannel'):
            update_data('CHENNEL_FOR_SEND_CONTENT', str(message.chat.id))
        if (data_is() and str(message.chat.id) != get_id_chennel_for_send_content()):
            send_media(get_id_moderator(), message)  # відправляємо мем модератору через обробник типу мема


# Пітвердження модератора через тег
# Модератор тегає повідомлення які сподобались
@app.on_message(filters.reply)
def moderator_cheak(_,message):
    #print(get_id_moderator())
    if(str(message.chat.id)==get_id_moderator()):
        print(message)
        # відправляємо на канал для контенту через обробник типу мема
        send_media(get_id_chennel_for_send_content(), message.reply_to_message)

        # видаляти повідомлення з придложки
        message.reply_to_message.delete()

        # видаляти повідомлення повідомлення про тег
        message.delete()


app.run()