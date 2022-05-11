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

def search_photo(user_owner_id):
    vk_ = vk_api.VkApi(token=token_user)
    try:
        response = vk_.method('photos.get',
                              {
                                  'access_token': token_user,
                                  'v': version,
                                  'owner_id': user_owner_id,
                                  'album_id': 'profile',
                                  'count': 10,
                                  'extended': 1,
                                  'photo_sizes': 1,
                              })
    except ApiError:
        return 'Нет доступа'
    users_photos = []
    for el in range(10):
        try:
            users_photos.append(
                [response['items'][el]['likes']['count'],
                 'photo' + str(response['items'][el]['owner_id']) + '_' + str(response['items'][el]['id'])])
        except IndexError:
            users_photos.append(['нет фото.'])
    return users_photos

def sort_likes(photos):
    result = []
    for element in photos:
        if element != ['нет фото.'] and photos != 'нет доступа к фото':
            result.append(element)
    return sorted(result)



#JSON
def create_json(lst):
    today = datetime.date.today()
    today_str = f'{today.day}.{today.month}.{today.year}'
    res = {}
    res_list = []
    for num, info in enumerate(lst):
        res['data'] = today_str
        res['first_name'] = info[0]
        res['second_name'] = info[1]
        res['link'] = info[2]
        res['id'] = info[3]
        res_list.append(res.copy())

    with open("result.json", "a", encoding='UTF-8') as write_file:
        json.dump(res_list, write_file, ensure_ascii=False)

    print(f'Данные записаны в json файл.')
