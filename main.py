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


@app.on_message(filters.sticker)
def reply_sticker(_, message):
    me='gerach'
    print(message)
    if(message.from_user.username!=me):
        if(message.sticker.file_id == const.STIKER_REPLY_RIGHT):
            file_id = open('left.webp', 'rb')
            app.send_sticker(message.chat.id, file_id, reply_to_message_id=message.message_id)

        if (message.sticker.file_id == const.STIKER_REPLY_LEFT):
            file_id = open('right.webp', 'rb')
            app.send_sticker(message.chat.id, file_id, reply_to_message_id=message.message_id)


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


def update_data(what_update, id):
    try:
        with open('data.json') as f:
            data=json.load(f)
            data[what_update]=id

        with open('data.json', 'w') as f:
            json.dump(data, f)

    except:
        data = {'MODERATOR': '','CHENNEL_FOR_SEND_CONTENT':''}
        with open('data.json', 'w') as f:
            json.dump(data, f)

        return update_data(what_update,id)



def get_id_moderator():
    f = open('data.json')
    data = json.load(f)
    f.close()
    return data['MODERATOR']


def get_id_chennel_for_send_content():
    f = open('data.json')
    data = json.load(f)
    f.close()
    return data['CHENNEL_FOR_SEND_CONTENT']


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


def send_media(where, message):
    if (message.photo):
        
        app.download_media(message, file_name='photo.jpg')
        # message.download(file_name='photo.jpg')
        file_id = open('downloads/photo.jpg', 'rb')

        if (message.caption):
            app.send_photo(where, file_id, caption=message.caption)
        else:
            app.send_photo(where, file_id)
        os.remove("downloads/photo.jpg")
        file_id.close()

    elif(message.animation):
        app.download_media(message, file_name='giv.mp4')

        file_id = open('downloads/giv.mp4', 'rb')

        app.send_animation(where , file_id)
        os.remove("downloads/giv.mp4")
        file_id.close()

    elif (message.video and int(message.video.file_size)<20971520):

        app.download_media(message, file_name='video.mp4')

        file_id = open('downloads/video.mp4', 'rb')
        if (message.caption):
            app.send_video(where, file_id, caption=message.caption)
        else:
            app.send_video(where, file_id)

        os.remove("downloads/video.mp4")
        file_id.close()



@app.on_message(filters.command("newmoder", prefixes=".") & filters.me & filters.private)
def new_moder(_,message):
    #print(message.chat.id)
    update_data('MODERATOR',  str(message.chat.id))


@app.on_message(filters.command("newchannel", prefixes=".") & filters.me)
def new_channel(_,message):
    #print(message.chat)
    update_data('CHENNEL_FOR_SEND_CONTENT',  str(message.chat.id))

@app.on_message(filters.channel)
def parsing_chennel(_,message):
    #print('Send chennel')
    #print(message)
    if(message.reply_markup):
        if (cheack_mem(message.photo.file_id)):
            return None
        else:
            if(message.text=='.newchannel'):
                update_data('CHENNEL_FOR_SEND_CONTENT', str(message.chat.id))
            if(data_is() and str(message.chat.id)!=get_id_chennel_for_send_content()):
                send_media(get_id_moderator(), message)
            add_new_badmems(message.photo.file_id)
    else:
        if (message.text == '.newchannel'):
            update_data('CHENNEL_FOR_SEND_CONTENT', str(message.chat.id))
        if (data_is() and str(message.chat.id) != get_id_chennel_for_send_content()):
            send_media(get_id_moderator(), message)



@app.on_message(filters.reply)
def moderator_cheak(_,message):
    #print(get_id_moderator())
    if(str(message.chat.id)==get_id_moderator()):
        print(message)
        send_media(get_id_chennel_for_send_content(), message.reply_to_message)


        message.reply_to_message.delete()

        message.delete()


app.run()
