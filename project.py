import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from main import find_persons, search_photo
from db import engine, Session, write_msg, register_user, add_user, add_user_photos, add_to_black_list, \
    check_db_user, check_db_black, check_db_favorites, check_db_master, delete_db_blacklist, delete_db_favorites
from vk_config import token_group

# Для работы с API VK
vk = vk_api.VkApi(token=token_group)
longpoll = VkLongPoll(vk)
# Для работы с БД
session = Session()
connection = engine.connect()


def loop_bot():
    for this_event in longpoll.listen():
        if this_event.type == VkEventType.MESSAGE_NEW:
            if this_event.to_me:
                message_text = this_event.text
                return message_text, this_event.user_id


