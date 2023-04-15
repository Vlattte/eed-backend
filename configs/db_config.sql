# Создание таблицы

'''
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
    step_status text
)
"""