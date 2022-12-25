import psycopg2
from psycopg2 import Error
# Создание таблицы
"""
CREATE TABLE test_table
(
	Id SERIAL PRIMARY KEY,
	session_id text,
	step_num smallint,
	actions_per_step smallint, 
	attempts_left smallint
)
"""
# Параметры для подключения к БД
connect_params = {"user": "postgres", # пароль, который указали при установке PostgreSQL
                  "database":'test_db',
                  "password":"Admin",
                  "host":"localhost",
                  "port":"5432"} 


def get_session_id_list():
    # Функция возвращает список session_id, хранящихся в таблице
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(**connect_params)

        cursor = connection.cursor()
        cursor.execute(
            "SELECT session_id FROM test_table;"
        )
        list_id = cursor.fetchall()
        cursor.close()
        if list_id == None:
            return tuple()
        return [id[0] for id in list_id]
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            connection.close()

def write_row(session_id, step_num, actions_for_step, attempts_left):
    # Функция для записи о действии пользователя в таблицу
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(**connect_params)

        cursor = connection.cursor()
        if step_num == 0:
            cursor.execute(
                f"""
                    INSERT INTO test_table (session_id, step_num, actions_per_step, attempts_left)
                    VALUES('{session_id}', {step_num}, {actions_for_step}, {attempts_left})
                """
            )
        elif step_num >= 1:
            cursor.execute(
                f"""
                    UPDATE test_table SET step_num = {step_num}, 
                    actions_per_step = {actions_for_step}, attempts_left = {attempts_left}
                    WHERE session_id = '{session_id}'
                """
            )
        cursor.close()
        connection.commit()
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            connection.close()

def get_step_attempts(session_id):
    # Функция возвращает номер шага и количество попыток для его прохождения для заданного пользователя
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(**connect_params)

        cursor = connection.cursor()
        cursor.execute(
            f"""
            SELECT step_num, attempts_left FROM test_table 
            WHERE id = (SELECT MAX(id) FROM test_table WHERE session_id = '{session_id}')
            """
        )
        step, left_attempts = cursor.fetchone()
        cursor.close()
        return step, left_attempts
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            connection.close()