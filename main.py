import requests
import vk_api
import json
import datetime
from vk_api.tools import VkTools
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.exceptions import ApiError
from vk_config import version, token_user, group_id, token_group

#для запросов
url = 'https://api.vk.com/method/'

# авторизация
vk = vk_api.VkApi(token=token_group)
tools = VkTools(vk)

# для проверки
age_input = input("Введите верхнюю границу возраста: ")
user_choice = input("Кого ищем? 1 - женщина, 2 -мужчина ")
status = 1
age_from = 18

# поиск по критериям методом users.search и получение id
def find_persons(sex, age_at, age_to, city):
    ids_users = []
    vk_ = vk_api.VkApi(token=token_user)
    users_result = vk_.method('users.search',
            {
             'sort': 0,
              'has_photo': 1,
              'is_closed': False,
              'online': 0,
              'age_from': age_from,
              'age_to': age_input,
              'status': status,
              'sex': user_choice,
              'fields': 'city,photo,screen_name',
              'count': 10,
              'access_token': token_group,
              'v': version
                }).json()

#ищем в items элементы id и сохраняем
    for el in users_result['items']:
        users = [
            el['id']
            ]
        ids_users.append(users)
    return ids_users


#находим фото найденных людей методом photos.get

def search_photo(ids_users):
    founded_photo = []
    vk_ = vk_api.VkApi(token=token_user)
    photo_result = vk_.method(url + 'photos.get',
            {
            'owner_id': ids_users,
            'album_id': 'profile',
            'count': 10,
            'access_token': token_user,
            'v': version,
            'extended': 1,
            'photo_sizes': 1
            })

    for user_id, data in founded_photo.items():
        if data['count'] == 0:
            continue
        else:
            founded_photo[user_id] = []
            for photo in data['items']:
                founded_photo[user_id].append((
                    photo['likes']['count'],
                    photo['sizes'][-1]['url']
                ))

        if data['count'] > 3:
            founded_photo[user_id].sort(key=lambda x: (x[0], x[1]), reverse=True)
            founded_photo[user_id] = founded_photo[user_id][:3]

    return founded_photo
