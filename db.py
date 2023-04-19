import psycopg2
from psycopg2 import Error
import json


# Создание таблицы
"""
CREATE TABLE test_table
(
	Id SERIAL PRIMARY KEY,
	session_id text,
	step_num smallint,
	actions_per_step smallint, 
	sub_steps json, 
	attempts_left smallint,
	is_training text,
    ex_id text,
    app_el_count json,
    step_status text
)
"""
# Параметры для подключения к БД
connect_params = {"user": "postgres",  # пароль, который указали при установке PostgreSQL
                  "database": "test_db",
                  "password": "123",
                  "host": "localhost",
                  "port": "5433"}


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
    # finally:
    #     if connection:
    #         connection.close()

def write_row(session_id, step_num, actions_for_step, sub_steps, attempts_left, ex_id,
              is_training=True, step_status="default_step"):
    # Функция для записи о действии пользователя в таблицу
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(**connect_params)

        cursor = connection.cursor()
        if step_num == 0:
            cursor.execute(
                f"""
                    INSERT INTO test_table (session_id, step_num, actions_per_step, sub_steps, attempts_left, 
                    is_training, ex_id, step_status)
                    VALUES('{session_id}', {step_num}, {actions_for_step},
                            '{json.dumps(sub_steps)}', {attempts_left}, {is_training}, {ex_id}, '{step_status}')
                """
            )
        elif step_num >= 1:
            cursor.execute(
                f"""
                    UPDATE test_table SET step_num = {step_num}, 
                    actions_per_step = {actions_for_step}, sub_steps = '{json.dumps(sub_steps)}', 
                    attempts_left = {attempts_left}, ex_id = {ex_id}, step_status = '{step_status}'
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

def UpdateSingleField(field_name,  field_value, session_id, step_num):
    # Функция для записи о действии пользователя в таблицу
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(**connect_params)

        cursor = connection.cursor()
        if step_num == 0:
            #  это сломано, не трогать
            cursor.execute(
                f"""
                        INSERT INTO test_table ({field_name}) VALUES ({field_value})
                """
            )
        elif step_num >= 1:
            cursor.execute(
                f"""
                        UPDATE test_table SET {field_name} = '{field_value}'
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
            SELECT step_num, attempts_left, actions_per_step, sub_steps, is_training, step_status FROM test_table 
            WHERE id = (SELECT MAX(id) FROM test_table WHERE session_id = '{session_id}')
            """
        )
        step, left_attempts, left_steps, sub_steps, is_training, step_status = cursor.fetchone()
        cursor.close()
        return step, left_attempts, left_steps, sub_steps, is_training, step_status
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            connection.close()

def get_ex_id(session_id):
    try:
        connection = psycopg2.connect(**connect_params)

        cursor = connection.cursor()
        cursor.execute(
            f"""
            SELECT ex_id FROM test_table 
            WHERE id = (SELECT MAX(id) FROM test_table WHERE session_id = '{session_id}')
            """
        )
        ex_id = cursor.fetchone()
        cursor.close()
        return ex_id[0]
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            connection.close()

def is_field_exists(session_id, field_name):
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(**connect_params)

        cursor = connection.cursor()
        cursor.execute(
            f"""
            SELECT {field_name} FROM test_table 
            WHERE id = (SELECT MAX(id) FROM test_table WHERE session_id = '{session_id}')
            """
        )
        field_value = cursor.fetchone()
        cursor.close()
        if len(field_value[0]) == 1:
            if field_value[0]["name"] == "nan":
                return False
        else:
            return True
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            connection.close()


def get_field_data(session_id, field_name):
    try:
        # Подключение к существующей базе данных
        connection = psycopg2.connect(**connect_params)

        cursor = connection.cursor()
        cursor.execute(
            f"""
               SELECT {field_name} FROM test_table 
               WHERE id = (SELECT MAX(id) FROM test_table WHERE session_id = '{session_id}')
            """
        )
        field_value = cursor.fetchone()
        cursor.close()
        return field_value[0]
    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            connection.close()
