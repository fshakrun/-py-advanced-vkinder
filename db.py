import vk_api
from vk_api.longpoll import VkLongPoll
from vk_config import token_group
from random import randrange
import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, InvalidRequestError

# Подключение к базе
Base = declarative_base()
engine = sq.create_engine()
Session = sessionmaker(bind=engine)

# Работа с VK
vk = vk_api.VkApi(token=token_group)
longpoll = VkLongPoll(vk)

# Работа с базой
session = Session()
connection = engine.connect()

# Пользователь бота
class MainUser(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)

# Избранное
class Favorites(Base):
    __tablename__ = 'favorites'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String)
    second_name = sq.Column(sq.String)
    city = sq.Column(sq.String)
    link = sq.Column(sq.String)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id', ondelete='CASCADE'))


# Фото Избранное
class FavoritesPics(Base):
    __tablename__ = 'favorites_pics'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    link_photo = sq.Column(sq.String)
    count_likes = sq.Column(sq.Integer)
    id_dating_user = sq.Column(sq.Integer, sq.ForeignKey('favorites.id', ondelete='CASCADE'))


# Черный список
class BlackListed(Base):
    __tablename__ = 'black_listed'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String)
    second_name = sq.Column(sq.String)
    city = sq.Column(sq.String)
    link = sq.Column(sq.String)
    link_photo = sq.Column(sq.String)
    count_likes = sq.Column(sq.Integer)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id', ondelete='CASCADE'))


#Работа с Базой Данных


# Удаление из ЧС
def delete_db_blacklist(ids):
    current_user = session.query(BlackListed).filter_by(vk_id=ids).first()
    session.delete(current_user)
    session.commit()


# Удаление из Избранного
def delete_db_favorites(ids):
    current_user = session.query(Favorites).filter_by(vk_id=ids).first()
    session.delete(current_user)
    session.commit()


# Проверка на регистрацию пользователя
def check_db_master(ids):
    current_user_id = session.query(MainUser).filter_by(vk_id=ids).first()
    return current_user_id


# Проверка на наличие пользователя в БД
def check_db_user(ids):
    favorite_user = session.query(Favorites).filter_by(
        vk_id=ids).first()
    blocked_user = session.query(Favorites).filter_by(
        vk_id=ids).first()
    return favorite_user, blocked_user


# Проверка на наличие в ЧС
def check_db_black(ids):
    current_users_id = session.query(MainUser).filter_by(vk_id=ids).first()
    # Находим все анкеты из избранного которые добавил данный юзер
    all_users = session.query(BlackListed).filter_by(id_user=current_users_id.id).all()
    return all_users


# Проверка на наличие в Избранном
def check_db_favorites(ids):
    current_users_id = session.query(MainUser).filter_by(vk_id=ids).first()
    # Добавленные в Избранное
    alls_users = session.query(Favorites).filter_by(id_user=current_users_id.id).all()
    return alls_users


# Отправка сообщения пользователю
def write_msg(user_id, message, attachment=None):
    vk.method('messages.send',
              {'user_id': user_id,
               'message': message,
               'random_id': randrange(10 ** 7),
               'attachment': attachment})


# Регистрация в боте
def register_user(vk_id):
    try:
        new_user = MainUser(
            vk_id=vk_id
        )
        session.add(new_user)
        session.commit()
        return True
    except (IntegrityError, InvalidRequestError):
        return False


# Добавление пользователя в БД
def add_user(event_id, vk_id, first_name, second_name, city, link, id_user):
    try:
        new_user = Favorites(
            vk_id=vk_id,
            first_name=first_name,
            second_name=second_name,
            city=city,
            link=link,
            id_user=id_user
        )
        session.add(new_user)
        session.commit()
        write_msg(event_id,
                  'Пользователь добавлен в избранное')
        return True
    except (IntegrityError, InvalidRequestError):
        write_msg(event_id,
                  'Пользователь уже в избранном.')
        return False


# Сохранение в БД фото добавленного пользователя
def add_user_photos(event_id, link_photo, count_likes, id_dating_user):
    try:
        new_user = FavoritesPics(
            link_photo=link_photo,
            count_likes=count_likes,
            id_dating_user=id_dating_user
        )
        session.add(new_user)
        session.commit()
        write_msg(event_id,
                  'Фотография добавлена в Избранное')
        return True
    except (IntegrityError, InvalidRequestError):
        write_msg(event_id,
                  'Не получается добавить фото')
        return False


# Добавление в ЧС
def add_to_black_list(event_id, vk_id, first_name, second_name, city, link, link_photo, count_likes, id_user):
    try:
        new_user = BlackListed(
            vk_id=vk_id,
            first_name=first_name,
            second_name=second_name,
            city=city,
            link=link,
            link_photo=link_photo,
            count_likes=count_likes,
            id_user=id_user
        )
        session.add(new_user)
        session.commit()
        write_msg(event_id,
                  'Пользователь добавлен в ЧС.')
        return True
    except (IntegrityError, InvalidRequestError):
        write_msg(event_id,
                  'Пользователь уже находится в ЧС.')
        return False


if __name__ == '__main__':
    Base.metadata.create_all(engine)
