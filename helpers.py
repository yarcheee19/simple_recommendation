from typing import List, Optional
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor

from models import User, Post, Feed

def get_user(conn: connection, user_id: int) -> Optional[User]:
    """
    Загружает одного пользователя из базы данных по его Id.

    Возвращает объект User, если пользователь найден.
    Если пользователь с таким id отсутствует — возвращает None.
    """
    # TODO: Написать SQL-запрос для получения пользователя по user_id
    query = """
            SELECT * FROM public.user
            WHERE id = %s
            """

    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(query, (user_id,))
        row = cur.fetchone()

        # TODO: Преобразовать результат в объект User, если строка найдена
        return User(**row) if row is not None else None


def get_post(conn: connection, post_id: int) -> Optional[Post]:
    """
    Загружает один пост из базы данных по его Id.

    Возвращает объект Post, если пост найден.
    Если пост с таким id отсутствует — возвращает None.
    """
    # TODO: Написать SQL-запрос для получения поста по post_id
    query = """
            SELECT * FROM public.post
            WHERE id = %s
            """

    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(query, (post_id,))
        row = cur.fetchone()

        # TODO: Преобразовать результат в объект Post, если строка найдена
        return Post(**row) if row is not None else None


def get_feed(
    conn: connection, user_id: int = None, post_id: int = None, limit: int = 10
) -> List[Feed]:
    """
    Получает список действий пользователей с постами, включая данные о пользователях и постах.

    - Необходимо указать хотя бы один фильтр: user_id или post_id.
    - Возвращает не более `limit` записей.
    - Действия сортируются по времени: от самых свежих к более старым.
    - Используется для получения последних активностей пользователя или взаимодействий с постом.
    """
    if user_id is None and post_id is None:
        raise ValueError("Необходимо указать хотя бы user_id или post_id")

    # TODO: Написать SQL-запрос:
    # - выбрать данные из feed_action
    # - JOIN с user и post
    # - фильтрация по user_id / post_id (если заданы)
    # - сортировка по времени (DESC)
    # - ограничение по LIMIT
    query = """
            SELECT f.user_id, f.post_id, f.time, f.action, u.id AS id_user, u.gender, u.age, u.country, u.city, u.exp_group, u.os, u.source, p.id AS id_post, p.text, p.topic FROM public.feed_action AS f
            JOIN public.user AS u ON f.user_id = u.id
            JOIN public.post AS p ON f.post_id = p.id
            WHERE (%s IS NULL OR user_id = %s) AND (%s IS NULL OR post_id = %s)
            ORDER BY f.time DESC
            LIMIT %s
            """

    result = []
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(query, (user_id, user_id, post_id, post_id, limit,))
        #row = cur.fetchone()
        for row in cur:
            row = Feed(
                row["user_id"], 
                row["post_id"], 
                User(row["id_user"], row["gender"], row["age"], row["country"], row["city"], row["exp_group"], row["os"], row["source"]), 
                Post(row["id_post"], row["text"], row["topic"]), 
                row["action"],
                row["time"]
            ) 
            result.append(row) 

    return result


def get_recommended_feed(conn: connection, id: int, limit: int) -> List[Post]:
    """
    Возвращает список top-N постов с наибольшим числом лайков.

    Это базовая реализация рекомендательной системы (baseline),
    которая не учитывает индивидуальные предпочтения, а показывает
    одинаковые популярные посты всем пользователям.

    Параметры:
        conn (connection): подключение к базе данных.
        id (int): ID пользователя (в этой версии не используется,
                но оставлен для совместимости с будущей логикой).
        limit (int): количество постов в выдаче.

    Возвращает:
        List[Post]: список объектов Post, отсортированных по убыванию популярности.
    """
    # TODO: Написать SQL-запрос для выбора top-N постов с наибольшим числом лайков
    query = """
            SELECT p.id, p.text, p.topic FROM public.post AS p
            JOIN feed_action AS f ON p.id = f.post_id
            WHERE action = 'like'
            GROUP BY p.id
            ORDER BY COUNT(*) DESC
            LIMIT %s
            """
            
    
    with conn.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(query, (limit,))
        rows = cur.fetchall()
    result = []
    for row in rows:
        result.append(Post(**row))
    # TODO: Преобразовать строки в список объектов Post
    return result
