import re
import vk_api
import gspread
import _thread
import requests
from copy import copy
from time import sleep
from telebot import types
from telegraph import upload
from datetime import datetime
from fake_headers import Headers
from additional.objects import thread_exec as executive
from oauth2client.service_account import ServiceAccountCredentials
from additional.objects import start_main_bot, start_message, printer

stamp1 = int(datetime.now().timestamp())
params = {
    'access_token': 'ca876787ca876787ca876787aacaf5d7becca87ca876787946bb00f4f54b680d843283b',
    'v': '5.110',
    'domain': 'fan_arthas',
    'count': 100
}
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
bot = start_main_bot('non-async', '587974580:AAFGcUwspPdr2pU44nJqLD-ps9FxSwUJ6mg')
start_message = start_message(stamp1)
idMainChannel = -1001354415399
idMe = 396978030
used_links = []


def vk_parser():
    global used_links
    sleep(20)
    while True:
        try:
            sleep(10)
            response = requests.get('https://api.vk.com/method/wall.get', params=params).json()
            for item in reversed(response['response']['items']):
                post = 'https://vk.com/' + params['domain'] + '?w=wall' + str(item['owner_id']) + '_' + str(item['id'])
                if post not in used_links:
                    sleep(10)
                    used_links.append(post)
                    printer('получена ' + post)
                    if item.get('copy_history') is None:
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
                                            vk_session = vk_api.VkApi('+375292001283', 'vk_Evolve_new)_12600')
                                            vk = vk_session.get_api()
                                            vk_session.auth()
                                            video = vk.video.get(owner_id=owner_id, videos=link)['items'][0]
                                            if video.get('platform') in [None, 'YouTube']:
                                                if video.get('platform') == 'YouTube':
                                                    link = re.sub('\?.*', '', video['player'])
                                                    link = re.sub('www.youtube.com/embed', 'youtu.be', link)
                                                    group.append({'type': 'YouTube', 'content': link})
                                                else:
                                                    response = requests.get(video['player'], headers=headers)
                                                    search = list(
                                                        reversed(re.findall('"cache\d+":"(.*?)"', response.text)))
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
                                        text = '<a href="https://telegra.ph' + uploaded[0] + '">​​ </a>' + text[:4090]
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
                                text = '<a href="' + file_name + '"> </a>' + text[:4090]
                                group.clear()
                        if len(group) == 0:
                            bot.send_message(idMainChannel, text[:4096], parse_mode='HTML')
        except IndexError and Exception:
            executive()


def google():
    global used_links
    try:
        cred1 = ServiceAccountCredentials.from_json_keyfile_name('worker5-storage.json', scope)
        client1 = gspread.authorize(cred1)
        used_links = client1.open('vk_fan').worksheet('main').col_values(1)
    except IndexError and Exception:
        used_links = []
        executive()
    while True:
        try:
            cred1 = ServiceAccountCredentials.from_json_keyfile_name('worker5-storage.json', scope)
            client1 = gspread.authorize(cred1)
            worksheet = client1.open('vk_fan').worksheet('main')
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
