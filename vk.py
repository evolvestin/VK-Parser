import os
import re
import vk_api
import gspread
import _thread
import objects
import requests
from copy import copy
from time import sleep
from telebot import types
from telegraph import upload
from fake_headers import Headers
from objects import thread_exec as executive
stamp1 = objects.time_now()
params = {
    'access_token': os.environ['VK_TOKEN'],
    'v': '5.110',
    'domain': os.environ['address'],
    'count': 100}
used_links = []
idMe = 396978030
idMainChannel = -1001186759363
objects.environmental_files()

bot = objects.start_main_bot('non-async', os.environ['TOKEN'])
if os.environ.get('api'):
    idMainChannel = -1001354415399
    start_message = objects.start_message(os.environ['TOKEN'], stamp1)


def telegram_publish(item):
    group = []
    text = None
    caption = None
    if item.get('text'):
        text = re.sub('<', '&#60;', item.get('text'))
        text = re.sub('youtu.be/', 'www.youtube.com/watch?v=', text)
    if item.get('attachments'):
        if len(item.get('attachments')) > 0:
            number = 0
            for media in item.get('attachments'):
                number += 1
                headers = Headers(headers=True).generate()
                if media['type'] in ['photo', 'video', 'doc']:
                    if media['type'] == 'photo':
                        file_name = str(number) + '.jpg'
                        sizes = media['photo']['sizes']
                        photo = sizes[len(sizes) - 1]
                        request = requests.get(photo['url'], headers=headers)
                        with open(file_name, 'wb') as file:
                            file.write(request.content)
                        group.append({'type': 'photo', 'content': open(file_name, 'rb')})

                    elif media['type'] == 'video':
                        video = media['video']
                        owner_id = str(video['owner_id'])
                        link = owner_id + '_' + str(video['id']) + '_' + video['access_key']
                        vk_session = vk_api.VkApi(os.environ['phone'], os.environ['vk_pass'])
                        vk = vk_session.get_api()
                        vk_session.auth()
                        video = vk.video.get(owner_id=owner_id, videos=link)['items'][0]
                        if video.get('platform') in [None, 'YouTube']:
                            if video.get('platform') == 'YouTube':
                                link = re.sub(r'\?.*', '', video['player'])
                                link = re.sub('www.youtube.com/embed', 'youtu.be', link)
                                group.append({'type': 'YouTube', 'content': link})
                            else:
                                response = requests.get(video['player'], headers=headers)
                                search = list(
                                    reversed(re.findall(r'"cache\d+":"(.*?)"', response.text)))
                                if search:
                                    file_name = str(number) + '.mp4'
                                    request = requests.get(re.sub(r'\\', '', search[0]))
                                    with open(file_name, 'wb') as file:
                                        file.write(request.content)
                                    group.append(
                                        {'type': 'video', 'content': open(file_name, 'rb')})
                    else:
                        file_name = str(number) + '.gif'
                        if media['doc']['ext'] == 'gif':
                            request = requests.get(media['doc']['url'], headers=headers)
                            with open(file_name, 'wb') as file:
                                file.write(request.content)
                            group.append({'type': 'gif', 'content': open(file_name, 'rb')})
    if len(group) > 1:
        media_group = []
        for media in group:
            if media['type'] != 'YouTube':
                caption = None
                if media['type'] == 'photo':
                    func = types.InputMediaPhoto
                else:
                    func = types.InputMediaVideo
                if len(media_group) == 0 and text:
                    caption = text[:1024]
                media_group.append(func(media['content'], caption=caption, parse_mode='HTML'))
            else:
                video_id = re.sub('https://youtu.be/', '', media['content'])
                if text.startswith('<a'):
                    if video_id not in text:
                        text += '\nhttps://www.youtube.com/watch?v=' + video_id
                else:
                    text = '<a href="' + media['content'] + '"> </a>' + text
        if media_group:
            bot.send_media_group(idMainChannel, media_group)
        else:
            group.clear()
    if len(group) == 1:
        media = group[0]
        file_name = media['content']
        if type(media['content']) != str:
            file_name = media['content'].name
        if text:
            if len(text) >= 1024:
                caption = None
                try:
                    uploaded = upload.upload_file(open(file_name, 'rb'))
                    text = '<a href="https://telegra.ph' + uploaded[0] + '"></a>' + text[:4090]
                except IndexError and Exception:
                    caption = text[:1024]
            else:
                caption = text[:1024]
        if media['type'] != 'YouTube':
            if text and caption is None:
                group.clear()
            else:
                if media['type'] == 'photo':
                    func = bot.send_photo
                elif media['type'] == 'video':
                    func = bot.send_video
                else:
                    func = bot.send_document
                func(idMainChannel, open(file_name, 'rb'), caption=caption, parse_mode='HTML')
        else:
            text = objects.html_link(file_name, ' ') + text[:4090]
            group.clear()
    if len(group) == 0:
        bot.send_message(idMainChannel, text[:4096], parse_mode='HTML')


def vk_parser():
    global used_links
    while not used_links:
        sleep(1)
    while True:
        try:
            sleep(20)
            response = requests.get('https://api.vk.com/method/wall.get', params=params).json()
            if response.get('response'):
                for item in reversed(response['response']['items']):
                    post = 'https://vk.com/' + params['domain'] + \
                        '?w=wall' + str(item['owner_id']) + '_' + str(item['id'])
                    if post not in used_links:
                        used_links.append(post)
                        objects.printer('получена ' + post)
                        if item.get('copy_history') is None:
                            telegram_publish(item)
                        sleep(10)
            else:
                if response.get('error'):
                    objects.printer(response)
                    sleep(180)
        except IndexError and Exception:
            executive()


def google():
    global used_links
    try:
        client = gspread.service_account('worker5-storage.json')
        used_links = client.open('vk_fan').worksheet('main').col_values(1)
        while True:
            client = gspread.service_account('worker5-storage.json')
            worksheet = client.open('vk_fan').worksheet('main')
            values = worksheet.col_values(1)
            for value in copy(used_links):
                if value not in values:
                    worksheet.insert_row([value], 1)
                    sleep(2)
            sleep(5)
    except IndexError and Exception:
        executive()


@bot.message_handler(func=lambda message: message.text)
def repeat_all_messages(message):
    try:
        if message.chat.id == idMe:
            doc = open('log.txt', 'rt')
            bot.send_document(message.chat.id, doc)
            doc.close()
    except IndexError and Exception:
        executive(str(message))


def telegram_polling():
    try:
        bot.polling(none_stop=True, timeout=60)
    except IndexError and Exception:
        bot.stop_polling()
        sleep(1)
        telegram_polling()


if __name__ == '__main__':
    _thread.start_new_thread(vk_parser, ())
    _thread.start_new_thread(google, ())
    telegram_polling()
