# Парсер групп [vk.com](https://vk.com/)
Собственно, скрипт парсера стены любой группы ВК.
Однажды мне понадобилось парсить группу ВК одной известной личности, создав клон группы
в Telegram. Погуглив, я не особо нашел нормальных парсеров, возможно плохо искал, но все же решил написать свой.

Обратившись к довольно странно выполненной, но если разобраться, удобной документации VK API (официальной).

1. Берет последних 100 постов в группе ВК.
2. Сверяет ссылки на посты с заранее записанными в гугл таблицах.
3. Определяет тип поста и постит его в канал или группу в Telegram.
   > Ох пришлось повозиться с форматами постов, но вроде все основные мы умеем. Картинки, видео, составные посты.
   > Не умеем в музыку, потому что ее анально модерируют и ВК возвращает довольно забавную запись в ответ на запрос.
   > Есть проблемы со скачиванием видео из ВК, там пришлось городить костыли и это не всегда работает, увы.
   > А вот если запощено видео из ютуба, то тут очень хорошо работает.

`Запуск был произведен 26.06.2020`
Канал в Telegram продвигать пока не решили когда будем, но контент идет, очень удобно.

`Последний апдейт` 05.11.2020. Добавил описание и улучшил секретность. Апдейты может будут когда-нибудь.
Во всяком случае, парсер удобный и работает стабильно, пригодится.

`последний апдейт` Оказывается забыл убрать номер телефона и пароль от вк. Причем в течении суток какие-то
боты их нашли, украли и попытались увести страницу вк. Будьте бдительны!

12.11.2020 Обновил библиотеку e-objects до версии 1.2.0

28.11.2022 Бот все еще работает. e-objects 1.2.0 перенесено в файл functions, 
чтобы можно было использовать e-objects версией повыше.
