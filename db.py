import psycopg2
from config import host, db_name, user, password, port


class BotDB:
    def __init__(self):
        """Инициализация соединения с БД."""
        self.conn = psycopg2.connect(host=host, port=port, user=user, password=password, database=db_name)
        self.cursor = self.conn.cursor()

    def new_table(self):
        """Создание таблицы."""
        self.cursor.execute("""CREATE TABLE users(
            id serial PRIMARY KEY,
            id_telegram integer,
            first_name varchar(50),
            last_name varchar(50),
            country varchar(50),
            phone varchar(50));""")
        self.conn.commit()

    def add_user(self, message):
        """Добавляем юзера."""
        self.cursor.execute(f'INSERT INTO USERS (id_telegram) VALUES ({message.chat.id})')
        return self.conn.commit()

    def update_name(self, message):
        """Обновляем данные юзера."""
        try:
            text = message.text.split()
            self.cursor.execute(f'Select id from USERS where id_telegram = {message.chat.id}')
            id = max(self.cursor.fetchall())[0]
            self.cursor.execute(
                f"UPDATE USERS SET (first_name, last_name) = ('{text[0]}', '{text[1]}') WHERE id = {id};")
            self.conn.commit()
            return str(id)
        except:
            return "Произошла ошибка, введите имя корректно"

    def update_phone(self, message, phone):
        """Обновляем данные юзера."""
        self.cursor.execute(f'Select id from USERS where id_telegram = {message.chat.id}')
        id = max(self.cursor.fetchall())[0]
        self.cursor.execute(f"UPDATE USERS SET phone = ('{phone}') WHERE id = {id};")
        self.conn.commit()

    def update_country(self, message, country):
        """Обновляем данные юзера."""
        self.cursor.execute(f'Select id from USERS where id_telegram = {message.chat.id}')
        id = max(self.cursor.fetchall())[0]
        self.cursor.execute(f"UPDATE USERS SET country = ('{country}') WHERE id = {id};")
        self.conn.commit()

    def drop_recorde(self, message):
        """Инициализация соединения с БД."""
        self.cursor.execute(f'Select id from USERS where id_telegram = {message.chat.id}')
        id = max(self.cursor.fetchall())[0]
        self.cursor.execute(f'DELETE from USERS where id = {id}')
        return self.conn.commit()

    def drop_null(self):
        """Удаление записи если заполнена не полностью."""
        self.cursor.execute(
            'Select id from USERS where id_telegram is null ||'
            'first_name is null || last_name is null || phone is null ||'
            'country is null or (last_name is null AND first_name is null)'
        )
        id = self.cursor.fetchall()
        list_id = []
        if len(id) > 0:
            if len(id) > 1:
                for i in id:
                    list_id.append(i[0])
                list_id = tuple(list_id)
                self.cursor.execute(f'DELETE from USERS where id IN {list_id}')
            else:
                self.cursor.execute(f'DELETE from USERS where id = {id[0][0]}')
            return self.conn.commit()

    def user_exist(self, message):
        """Проверяем был ли юзер зарегестрирован ранее."""
        self.cursor.execute(f'Select * from USERS where id_telegram = {message.chat.id}')
        data = self.cursor.fetchall()
        data = True if (data != []) else False
        return data

    def get_last_record(self, message):
        """Получаем последнюю актуальную запись."""
        self.cursor.execute(f'Select id from USERS where id_telegram = {message.chat.id}')
        id = max(self.cursor.fetchall())[0]
        self.cursor.execute(f'Select * from USERS where id = {id}')
        return self.cursor.fetchall()

    def get_record(self, message):
        """Получае все записи пользователя."""
        self.cursor.execute(f'Select * from USERS where id_telegram = {message.chat.id}')
        return self.cursor.fetchall()

    def drop(self, message):
        """Удаление записи по запросу пользователя."""
        id = int(message.text)
        self.cursor.execute(f"Select * from USERS where (id, id_telegram) = ('{id}', '{message.chat.id}')")
        data = self.cursor.fetchall()
        if data:
            self.cursor.execute(f'DELETE from USERS where id = {id}')
            self.conn.commit()
            return 'Запись успешна удалена'
        return 'Данной записи не существует или она была сделана не Вами'

    def close(self):
        """Закрытие соединения с БД."""
        self.cursor.close()
        self.conn.close()
