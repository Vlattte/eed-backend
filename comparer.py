import json
import db

import randomSteps

def GetInstruction(app, step_id): #app - аппаратура, step_id - номер шага
    instr_file = open(app, encoding='utf-8')
    data = json.load(instr_file)
    instr_file.close()

    for i in range(len(data)):
        if data["step_"+str(i)]["step"] == step_id:
            return data["step_"+str(i)]

# проверяет есть ли еще такой id в инструкции, то есть проверяет нужно ли убрать выделение желтым с элемента с этим id
def IsMoreSameId(id, instruction, db_steps, steps_count):
    for item in db_steps:
        for step in item:
            if item[step] == 'False':
                # значит этот шаг еще не сделан
                for i in range(steps_count):
                    if instruction["sub_steps"][i]["name"] == step:
                        # нашли не выполненный шаг, сравним наш ли это id
                        if instruction["sub_steps"][i]["action_id"] == id:
                            return True

    return False


# надо записать индексы из массива array_actions_for_step, в виде словаря по типу: "index": bool,
# где bool - сделан ли шаг под этим индексом
# в этом шаге может быть написан следующий шаг, значащий следующее положение этого же элемента
def CheckMultipleInstructions(session_id, instruction, message, left_attempts, step, left_steps, ex_id):
    # код возврата:
    # -1 - ошибка пользователя (status="incorrect")
    # 0 - остались еще под шаги (status="correct")
    # 1 - шаги кончились, все правильно (status="correct")
    # 2 - подшаги еще есть, но действия с текущим id закончились (status="progres")
    return_code = -1

    steps = instruction["actions_for_step"]
    sub_steps = []
    result = db.is_field_exists(session_id, "sub_steps")
    if not result:
        for i in range(steps):
            sub_steps.append({instruction["sub_steps"][i]["name"]: "False"})

        db.write_row(session_id=session_id,
                     step_num=step,
                     actions_for_step=instruction['actions_for_step'],
                     sub_steps=sub_steps,
                     attempts_left=left_attempts, 
                     ex_id=ex_id)
    else:
         sub_steps = db.get_field_data(session_id, "sub_steps")

    for i in range(steps):
        if instruction["sub_steps"][i]["action_id"] == message[1][1]:
            if str(instruction["sub_steps"][i]["current_value"]) == str(message[4][1]):
                name = instruction["sub_steps"][i]["name"]

                if sub_steps[i][name] == "False":
                    sub_steps[i][name] = "True"

                    # True, если остались еще действия с этим элементом
                    id = instruction["sub_steps"][i]["action_id"]
                    is_no_element_actions = IsMoreSameId(id, instruction, sub_steps, steps)
                    return_code = 0

                    if is_no_element_actions:
                        return_code = 2

                    print("LEFT = ")
                    print(left_steps)
                    if left_steps == 1:
                        return_code = 1
                    else:
                        db.write_row(session_id=session_id,
                                 step_num=step,
                                 actions_for_step=left_steps-1,
                                 sub_steps=sub_steps,
                                 attempts_left=left_attempts, 
                                 ex_id=ex_id)

    return return_code

def CheckRandomedValues(instruction, message):
    # 0 - остались еще под шаги (status="correct")
    # 1 - шаги кончились, все правильно (status="correct")
    return_code = 0

    steps = instruction["actions_for_step"]
    for i in range(steps):
        if instruction["sub_steps"][i]["action_id"] == message[1][1]:
            if str(instruction["sub_steps"][i]["current_value"]) == str(message[4][1]):
                return_code = 1

    return return_code


def GetAppName(app_id):
    if app_id == 1:
        return "P302O"

    return "P302O"



def IsForRandomStep(key_name):
    random_steps_file = open("random_exersices.json", encoding="utf-8")
    random_steps_names = json.load(random_steps_file)
    if key_name in random_steps_names["for_random"]:
        return True
    return False

def WhatExercise(message, session_id):
    is_training = "nan"
    app_id = 0
    exercise_name = ""
    full_id = "0"
    key_name = "ex_test"

    # проверяем флаг тренировки
    if message[1][0] == "is_training":
        is_training = message[1][1]
    
    exercise_json = open("id_json.json", encoding='utf-8')
    data = json.load(exercise_json)

    # id норматива
    if message[3][0] == "norm":

        full_id = message[3][1]
        if message[3][1] != "0":
            app_id = message[3][1][0]    # id оборуования
            ex_id = message[3][1][1:]  # id упражнения
            key_name = "ex_" + app_id + "_" + ex_id

    else:
        full_id = db.get_ex_id(session_id)
        app_id = full_id[0]
        ex_id = full_id[1:]
        key_name = "ex_" + app_id + "_" + ex_id

    # убрать когда будут доделаны карты
    # key_name = "ex_test"

    exercise_name = data[key_name]

    return exercise_name, is_training, full_id, key_name, app_id

def GetStepsFromJson(key_name):
    steps_json = open("steps_json.json", encoding='utf-8')
    data = json.load(steps_json)
    return data[key_name]

#[["session_id","1gjolm7fq"],["id",1015],["draggble",false],["rotatable",true],["currentValue",60],["left",249.99999999999997],["top",105.55555555555554]]
def Comparer(message): #message - json от фронта, app - аппаратура
    # по id норматива получаем название соответсвующего файла
    # так же получаем значение флага is_training

    # is_zero_step - True, если еще такого session_id нет
    # session_id - id
    # session_id_list
    # instruction
    # sub_steps

    is_zero_step = False
    session_id = message[0][1]
    session_id_list = db.get_session_id_list()
    instruction = {}

    # exercise_name
    # is_training
    # ex_id
    # key_name
    # app_id
    # например: key_name = "ex_1_1"; ex_id = 11; app_id = 1

    exercise_name, is_training, ex_id, key_name, app_id = WhatExercise(message, session_id)

    return_request = {}
    # Если session_id нет в таблице, то создаем запись для него и устанавливаем номер шага = 0
    if session_id not in session_id_list:
        # берем первый шаг, потому что count_next, может отличаться от actions_for_step

        instruction = GetInstruction(exercise_name, 1)
        sub_steps = {'name': 'nan'}
        is_zero_step = True
        db.write_row(session_id=session_id, 
                     step_num=0,
                     actions_for_step=instruction["actions_for_step"],
                     sub_steps=sub_steps,
                     attempts_left=1,
                     ex_id=ex_id,
                     is_training=is_training)

    if is_training != 'nan':
        # instruction = GetInstruction(exercise_name, 0)
        return_request = {'next_actions': instruction['next_actions']}

    step, left_attempts, left_sub_steps, sub_steps, is_training, step_status = db.get_step_attempts(session_id=session_id)

    if step == 0 and not is_zero_step:
        step = 1

    instruction = GetInstruction(exercise_name, step)

    # [0][1] - session_id
    # [1][1] - id
    # [2][1] - draggable (НЕ НУЖЕН, НО ПУСТЬ БУДЕТ)
    # [3][1] - rotatable (НЕ НУЖЕН)
    # [4][1] - currentValue
    # [5][1] - left
    # [6][1] - top

    steps_num = GetStepsFromJson(key_name)

    has_action = False
    array_actions = False

    # существует ли массив действий (зажечь лампочку, передвинуть стрелку)
    if "array_actions" in instruction:
        array_actions = instruction["array_actions"]

    # По умолчанию считаем, что отдаваемый ответ = False
    if instruction["count_action"] > 0:
        has_action = True

    return_request = {"validation": False,
                      "has_action": has_action,
                      "annotation":    instruction["annotation"],
                      "fail":       False,
                      "count_action":  instruction["count_action"],
                      "array_actions": array_actions,
                      "count_next":    instruction["count_next"],
                      "next_actions":  instruction["next_actions"],
                      "finish":     False,
                      "before_id":     instruction["before_id"],
                      "is_random_step": False,
                      "status": "incorrect"}
    

    isRandomStep = IsForRandomStep(key_name)
    if isRandomStep and step_status != "random_step_progress":
        random_step_instruction = GetInstruction(exercise_name, 1)

        app_name = GetAppName(app_id)
        prepare_action_values, prepare_random_values, sub_steps_num = \
            randomSteps.RandomPrepare(app_id, random_step_instruction, app_name)

        return_request["is_random_step"] = True
        return_request["random_values"] = prepare_random_values
        return_request["next_actions"] = prepare_action_values

        step_status = "random_step_progress"  # положения зарандомили, теперь обрабатываем шаги обработчиком рандомных шагов
        db.write_row(session_id=session_id,
                     step_num=1,
                     actions_for_step=sub_steps_num,
                     sub_steps=sub_steps,
                     attempts_left=1,
                     ex_id=ex_id,
                     is_training=is_training,
                     step_status=step_status)
        
    elif step_status == "random_step_progress":   
        random_step_instruction = GetInstruction(exercise_name, 1)
        random_status = CheckRandomedValues(instruction, message)
        if random_status == 1:
            return_request["status"] = "correct"
            # return_request["validation"] = True
            return_request["validation"] = False
            left_sub_steps -= 1
        else:
            return_request["status"] = "progres"
            return_request["validation"] = False

        if left_sub_steps == 0:
            step_status = "regular_steps"
            return_request["validation"] = True
        
        
        db.write_row(session_id=session_id,
                     step_num=1,
                     actions_for_step=left_sub_steps,
                     sub_steps=sub_steps,
                     attempts_left=1,
                     ex_id=ex_id,
                     is_training=is_training,
                     step_status=step_status)

    step_increm = 1
    multiple_res = 1

    if not is_zero_step and not isRandomStep:
        ###### MULTIPLE STEPS ######
        # multiple == несколько действий за шаг
        if instruction["id"] == "multiple":
            multiple_res = CheckMultipleInstructions(session_id, instruction, message, left_attempts, step, left_sub_steps, ex_id)

            # если еще есть подшаги и не было ошибки
            if multiple_res != -1:
                return_request["validation"] = False
                step_increm = 0
                # нужен для фронта, чтобы не заменять на одно и то же
                return_request["status"] = "correct"
            # если подшаги кончились
            if multiple_res == 1:
                step_increm = 1
                return_request["status"] = "correct"
                return_request["validation"] = True
            # все верно, шаг не закончен, но подсветку с элемента убирать не надо, т.к. с ним есть еще действия
            if multiple_res == 2:
                return_request["status"] = "progres"
                step_increm = 0
                return_request["validation"] = False


        ###### SINGLE STEP ######
        elif instruction["id"] == message[1][1]:  # element id
            if message[2][1]:  # is element draggable
                if abs(message[5][1] - instruction["left"]) <= 10:
                    if abs(message[6][1] - instruction["top"]) <= 10:
                        return_request["validation"] = True
                        return_request["status"] = "correct"
            else:
                if str(message[4][1]) == str(instruction["current_value"]):
                    return_request["validation"] = True
                    return_request["status"] = "correct"

        ###### ПРОВЕРКА НА ПРАВИЛЬНОСТЬ ДЕЙСТВИЯ ######
        if return_request['validation'] or return_request["status"] != "incorrect":        # если правильное действие
            print('Правильное действие')
            if step == steps_num+1 and multiple_res == 1:                       # если финальный шаг
                print('Карта пройдена')
                return_request['finish'] = True
                pass
            else:
                # если закончились подшаги
                if multiple_res == 1:
                    new_instruction = GetInstruction(exercise_name, step + 1)
                    sub_steps = {'name': 'nan'}
                    db.write_row(session_id=session_id,
                            step_num=step + step_increm,
                            actions_for_step=new_instruction['actions_for_step'],
                            sub_steps=sub_steps,
                            attempts_left=1, 
                            ex_id=ex_id)

        elif return_request['validation'] == False:
            print('Неправильное действие')
            if left_attempts == 1:
                print('Попытка провалена')
                return_request['fail'] = True
                pass
            else:
                #return_request['is_finished'] = True
                sub_steps = {'name': 'nan'}
                db.write_row(session_id=session_id, 
                        step_num=step, 
                        actions_for_step=instruction['actions_for_step'],
                        sub_steps=sub_steps,
                        attempts_left=left_attempts - 11, 
                        ex_id=ex_id)

    print(return_request)
    return return_request
